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
    torch.cuda.empty_cache()

    print(f"STATUS: loading backbone {args.model}...")
    model = YOLO(args.model)

    # 🔧 UI Reporting Callbacks
    def on_train_epoch_end(trainer):
        # We extract relevant metrics from the trainer object
        epoch = trainer.epoch + 1 # 1-indexed
        total = trainer.epochs
        metrics = trainer.label_loss_items(trainer.tloss, prefix='train')
        loss = float(metrics.get('train/box_loss', 0)) + float(metrics.get('train/cls_loss', 0)) + float(metrics.get('train/dfl_loss', 0))
        
        # Format: EPOCH:1:50:0.543
        # Which is EPOCH:Current:Total:Loss
        print(f"EPOCH:{epoch}:{total}:{loss:.4f}")
        
        # Validation metrics (available after the validation step in each epoch)
        if hasattr(trainer, 'metrics'):
            map50 = trainer.metrics.get('metrics/mAP50(B)', 0) # mAP 50
            # Format: METRIC:acc:85.2
            print(f"METRIC:acc:{map50*100:.2f}")

    model.add_callback("on_train_epoch_end", on_train_epoch_end)

    # Optimized config for Jetson Orin Nano (7.6GB shared CPU/GPU memory)
    train_config = {
        "batch": 1,        # Minimal batch — 640x640 with batch=2 OOMs on Orin Nano
        "workers": 0,      # In-process loading — worker subprocesses eat shared memory
        "freeze": 5,
        "cache": "disk",   # Disk cache instead of RAM — RAM competes with GPU on unified memory
        "patience": 20,
        "plots": False,
        "amp": True,       # FP16 training — saves memory (AMP check is monkey-patched above)
        "device": 0 if torch.cuda.is_available() else "cpu",
    }

    print(f"STATUS: Starting training for {args.epochs} epochs...")
    results = model.train(
        data=str(data_yaml.resolve()),
        epochs=args.epochs,
        imgsz=args.imgsz,
        **train_config
    )

    print("STATUS: Training complete.")

    # 3. Copy best.pt to local path immediately (always available for validation)
    local_dir = Path(__file__).parent
    best_pt = Path(f"{results.save_dir}/weights/best.pt")
    local_pt = local_dir / "best.pt"
    local_engine = local_dir / "best.engine"

    if best_pt.exists():
        shutil.copy2(best_pt, local_pt)
        print(f"RESULT_MODEL_PT:{best_pt}")
        print(f"RESULT_MODEL_LOCAL:{local_pt}")

    # Free training memory before TRT export
    del model
    torch.cuda.empty_cache()

    # 4. TensorRT export — SKIPPED on Orin Nano
    # The TRT engine builder OOMs on 7.6GB shared memory (needs ~12MB GPU alloc that
    # fails after training consumed most of it).  The C++ OOM crashes the subprocess
    # before Python's try/except can catch it, causing _on_train_finished to see a
    # non-zero exit code and skip validation.  Validation works fine with .pt.
    print("STATUS: TensorRT export skipped (Orin Nano memory). Using .pt for validation.")

    print("STATUS: Finished!")

if __name__ == "__main__":
    main()
