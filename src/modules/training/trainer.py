import os
import sys
import shutil
import random
import argparse
from pathlib import Path

# Fix: Ensure we use the right directory for the script
BASE_TRAIN_DIR = Path(__file__).parent / "detection"

def prepare_dataset(project_path: str, class_names: list):
    """Split the images from projects/data/[project] into train/val folders."""
    project_dir = Path(project_path)
    if not project_dir.exists():
        print(f"ERROR: Project directory {project_path} not found.")
        sys.exit(1)

    # 1. Clear existing training data
    for folder in ["train", "val"]:
        img_dir = BASE_TRAIN_DIR / folder / "images"
        lbl_dir = BASE_TRAIN_DIR / folder / "labels"
        if img_dir.exists(): shutil.rmtree(img_dir)
        if lbl_dir.exists(): shutil.rmtree(lbl_dir)
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)

    # 2. Collect all images
    all_images = list(project_dir.glob("*.jpg")) + list(project_dir.glob("*.png"))
    if not all_images:
        print("ERROR: No images found in dataset folder.")
        sys.exit(1)

    # 3. Split 80/20
    random.shuffle(all_images)
    split_idx = int(len(all_images) * 0.8)
    train_imgs = all_images[:split_idx]
    val_imgs = all_images[split_idx:]

    def copy_set(img_list, target_folder):
        for img_path in img_list:
            # Copy Image
            shutil.copy(img_path, BASE_TRAIN_DIR / target_folder / "images" / img_path.name)
            # Copy Label (.txt) if exists
            label_path = img_path.with_suffix(".txt")
            if label_path.exists():
                shutil.copy(label_path, BASE_TRAIN_DIR / target_folder / "labels" / label_path.name)

    print(f"STATUS: Splitting dataset ({len(train_imgs)} train, {len(val_imgs)} val)...")
    copy_set(train_imgs, "train")
    copy_set(val_imgs, "val")

    # 4. Generate dataset.yaml
    # We must use absolute paths for the YAML to be safe across different run working dirs
    dataset_yaml = BASE_TRAIN_DIR / "dataset.yaml"
    
    # Map class index to name
    # If users provide names like [Tag 0, Tag 1], we map them.
    # YOLO requires class indices starting from 0.
    yaml_content = f"""
path: {BASE_TRAIN_DIR.resolve().as_posix()}
train: train/images
val: val/images

names:
"""
    for i, name in enumerate(class_names):
        yaml_content += f"  {i}: {name}\n"

    dataset_yaml.write_text(yaml_content.strip())
    print(f"STATUS: dataset.yaml generated at {dataset_yaml}")
    return dataset_yaml

def main():
    parser = argparse.ArgumentParser(description="AI Coding Lab Backend Trainer")
    parser.add_argument("--model", type=str, required=True, help="Base .pt model path")
    parser.add_argument("--project_path", type=str, required=True, help="Project data source folder")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--names", type=str, required=True, help="Comma separated class names")
    parser.add_argument("--project_name", type=str, default="", help="Project name for saving model")

    args = parser.parse_args()
    class_names = [n.strip() for n in args.names.split(",")]

    print("STATUS: Initializing backend training...")
    
    # 1. Prepare Data
    data_yaml = prepare_dataset(args.project_path, class_names)

    # 2. Start YOLO Training
    try:
        from ultralytics import YOLO
        import torch
        # Skip the AMP check — it downloads an extra model and OOMs on Jetson Orin Nano.
        # AMP itself (FP16 training) is fine and saves memory; only the check is problematic.
        # Patch both the module-level function AND the local import in the trainer module.
        _amp_skip = lambda *args, **kwargs: True
        import ultralytics.utils.checks
        ultralytics.utils.checks.check_amp = _amp_skip
        import ultralytics.engine.trainer as _utrainer
        _utrainer.check_amp = _amp_skip
    except ImportError:
        print("ERROR: Ultralytics or Torch not found.")
        sys.exit(1)

    # Free GPU memory before loading model (PyQt app + thumbnails consume shared memory)
    # On Jetson Orin Nano, RAM and GPU memory are shared — aggressively free both
    import gc
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    gc.collect()

    # Detect GPU memory and choose device/imgsz accordingly.
    # On Orin Nano (7.6GB shared), the PyQt5 app + OS consume most memory.
    # CUDA OOM crashes at C level (uncatchable), so we must prevent it upfront.
    imgsz = args.imgsz
    use_device = 0 if torch.cuda.is_available() else "cpu"

    if torch.cuda.is_available():
        free_mb = torch.cuda.mem_get_info()[0] / (1024 * 1024)
        total_mb = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
        print(f"STATUS: GPU memory — {free_mb:.0f}MB free / {total_mb:.0f}MB total")

        if free_mb < 1500:
            # Not enough GPU memory even for 320x320 — fall back to CPU
            print(f"STATUS: GPU memory critically low ({free_mb:.0f}MB). Using CPU for training.")
            use_device = "cpu"
            imgsz = min(imgsz, 320)
        elif free_mb < 4500 and imgsz > 320:
            print(f"STATUS: Low GPU memory ({free_mb:.0f}MB free). Reducing imgsz from {imgsz} to 320.")
            imgsz = 320

    print(f"STATUS: loading backbone {args.model}...")
    model = YOLO(args.model)
    # Free memory consumed by model loading before training starts
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # UI Reporting Callbacks
    def on_train_epoch_end(trainer):
        epoch = trainer.epoch + 1
        total = trainer.epochs
        metrics = trainer.label_loss_items(trainer.tloss, prefix='train')
        loss = float(metrics.get('train/box_loss', 0)) + float(metrics.get('train/cls_loss', 0)) + float(metrics.get('train/dfl_loss', 0))
        print(f"EPOCH:{epoch}:{total}:{loss:.4f}")
        if hasattr(trainer, 'metrics'):
            map50 = trainer.metrics.get('metrics/mAP50(B)', 0)
            print(f"METRIC:acc:{map50*100:.2f}")

    model.add_callback("on_train_epoch_end", on_train_epoch_end)

    # Config matching proven train_code.py settings for Jetson Orin Nano
    # On Jetson, RAM = GPU memory (unified). cache=True eats GPU memory.
    # Dynamically choose batch/cache/workers based on available memory.
    _batch = 2
    _cache = "disk"  # Default to disk cache — safe on shared-memory Jetson
    _workers = 2

    if torch.cuda.is_available():
        free_mb = torch.cuda.mem_get_info()[0] / (1024 * 1024)
        if free_mb < 4500:
            _batch = 1
            _workers = 1
            print(f"STATUS: Tight GPU memory ({free_mb:.0f}MB free). Using batch=1, disk cache.")
        if free_mb >= 5000:
            _cache = True  # Only use RAM cache when memory is comfortable
            print(f"STATUS: Sufficient GPU memory ({free_mb:.0f}MB free). Using RAM cache.")

    train_config = {
        "batch": _batch,
        "workers": _workers,
        "freeze": 5,        # Freeze low-level features — faster convergence, less memory
        "cache": _cache,    # disk cache by default on Jetson (shared memory)
        "patience": 20,
        "plots": False,
        "exist_ok": True,   # Reuse run directory — prevents accumulating train dirs
        "amp": True,        # FP16 training — saves memory
        "device": use_device,
    }

    # Lower batch size when using CPU (slower, don't want to also OOM on RAM)
    if use_device == "cpu":
        train_config["batch"] = 1
        train_config["workers"] = 0
        train_config["cache"] = False

    print(f"STATUS: Starting training for {args.epochs} epochs at imgsz={imgsz} on {use_device}...")
    results = model.train(
        data=str(data_yaml.resolve()),
        epochs=args.epochs,
        imgsz=imgsz,
        **train_config
    )

    print("STATUS: Training complete.")

    # 3. Copy best.pt to local path
    local_dir = Path(__file__).parent
    best_pt = Path(f"{results.save_dir}/weights/best.pt")
    local_pt = local_dir / "best.pt"
    local_onnx = local_dir / "best.onnx"
    local_engine = local_dir / "best.engine"

    if best_pt.exists():
        shutil.copy2(best_pt, local_pt)
        print(f"RESULT_MODEL_PT:{best_pt}")
        print(f"RESULT_MODEL_LOCAL:{local_pt}")

    # Free ALL training memory before conversion
    del model
    del results
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    gc.collect()

    # ── 4. Convert PT → ONNX → TensorRT Engine (FP16) ───────────────
    # Done in-process so CUDA context stays alive (separate QProcess can't see GPU on Jetson)
    import time as _time

    print("STATUS: Converting to TensorRT Engine...")
    sys.stdout.flush()

    # Step 1: PT → ONNX
    print("CONVERT:[1/2] Exporting PT to ONNX...")
    sys.stdout.flush()
    try:
        export_model = YOLO(str(local_pt))
        export_model.export(format="onnx", imgsz=imgsz, half=False, opset=17)
        del export_model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # Find the onnx file (ultralytics may place it alongside the .pt)
        if not local_onnx.exists():
            for p in local_dir.glob("*.onnx"):
                shutil.move(str(p), str(local_onnx))
                break
        if not local_onnx.exists():
            onnx_candidate = best_pt.with_suffix(".onnx")
            if onnx_candidate.exists():
                shutil.copy2(onnx_candidate, local_onnx)

        onnx_size = local_onnx.stat().st_size / (1024 * 1024)
        print(f"CONVERT:  ONNX exported ({onnx_size:.1f} MB)")
    except Exception as e:
        print(f"CONVERT:  ONNX export failed: {e}")
        print("STATUS: Finished!")
        sys.exit(0)

    sys.stdout.flush()

    # Step 2: ONNX → TensorRT Engine (raw TRT API — proven on Jetson)
    print("CONVERT:[2/2] Building TensorRT engine (FP16, ~30-40s)...")
    sys.stdout.flush()
    try:
        import tensorrt as trt

        TRT_WORKSPACE_GB = 2
        TRT_OPT_LEVEL = 0

        logger = trt.Logger(trt.Logger.WARNING)
        builder = trt.Builder(logger)
        network = builder.create_network(
            1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
        )
        parser = trt.OnnxParser(network, logger)

        with open(str(local_onnx), "rb") as f:
            if not parser.parse(f.read()):
                for i in range(parser.num_errors):
                    print(f"CONVERT:  Parse error: {parser.get_error(i)}")
                print("STATUS: Finished!")
                sys.exit(0)

        config = builder.create_builder_config()
        config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, TRT_WORKSPACE_GB << 30)
        config.set_flag(trt.BuilderFlag.FP16)
        config.builder_optimization_level = TRT_OPT_LEVEL

        # Timing cache
        project_root = Path(__file__).resolve().parents[3]
        cache_file = project_root / "timing.cache"
        if cache_file.exists():
            with open(str(cache_file), "rb") as f:
                cache_data = f.read()
            cache = config.create_timing_cache(cache_data)
            config.set_timing_cache(cache, ignore_mismatch=True)

        t0 = _time.time()
        engine = builder.build_serialized_network(network, config)
        elapsed = _time.time() - t0

        if engine is None:
            print("CONVERT:  Engine build failed!")
            print("STATUS: Finished!")
            sys.exit(0)

        with open(str(local_engine), "wb") as f:
            f.write(engine)

        # Save timing cache for next time
        try:
            cache = config.get_timing_cache()
            with open(str(cache_file), "wb") as f:
                f.write(cache.serialize())
        except Exception:
            pass

        engine_size = local_engine.stat().st_size / (1024 * 1024)
        print(f"CONVERT:  Engine built ({engine_size:.1f} MB) [{elapsed:.1f}s]")
        print(f"RESULT_MODEL_ENGINE:{local_engine}")

    except Exception as e:
        print(f"CONVERT:  TensorRT build failed: {e}")

    print("STATUS: Finished!")

if __name__ == "__main__":
    main()
