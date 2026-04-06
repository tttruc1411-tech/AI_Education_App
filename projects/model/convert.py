"""
Convert YOLOv8n: PT → ONNX → TensorRT Engine (FP16)
Tối ưu cho Jetson Orin Nano Super (8GB shared RAM)

Thông số:
  - optimization_level=1: build ~2.8 phút, FPS giống level=3
  - workspace=2GB: an toàn cho 8GB shared RAM
  - FP16: tối ưu inference trên Jetson

Usage:
  python3 convert.py models/yolov8n.pt
  python3 convert.py runs/detect/train/weights/best.pt
"""
import tensorrt as trt
import sys
import os
import time
import gc

# ======================== CONFIG ========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
IMGSZ = 640
CACHE_FILE = os.path.join(BASE_DIR, "timing.cache")
OPTIMIZATION_LEVEL = 0   # 0=nhanh nhất (34s) | 1=2.8p | 3=8.7p — accuracy giống nhau
WORKSPACE_GB = 2          # 4GB crash trên 8GB shared RAM
# ========================================================


def export_onnx(pt_path):
    """PT → ONNX bằng ultralytics"""
    from ultralytics import YOLO

    onnx_path = pt_path.replace(".pt", ".onnx")
    print(f"[1/2] PT → ONNX: {pt_path}")

    model = YOLO(pt_path)
    t0 = time.time()
    model.export(format="onnx", imgsz=IMGSZ, half=False, opset=17)
    elapsed = time.time() - t0

    if not os.path.exists(onnx_path):
        base = os.path.basename(pt_path).replace(".pt", ".onnx")
        for root, dirs, files in os.walk(os.path.dirname(pt_path) or "."):
            if base in files:
                onnx_path = os.path.join(root, base)
                break

    size = os.path.getsize(onnx_path) / 1024 / 1024
    print(f"  -> {onnx_path} ({size:.1f} MB) [{elapsed:.1f}s]")

    # Giải phóng GPU memory trước khi build TRT
    del model
    gc.collect()
    try:
        import torch
        torch.cuda.empty_cache()
    except:
        pass

    return onnx_path


def build_engine(onnx_path, engine_path):
    """ONNX → TensorRT Engine (FP16)"""
    print(f"[2/2] ONNX → TensorRT Engine (FP16, opt_level={OPTIMIZATION_LEVEL})")

    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(
        1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
    )
    parser = trt.OnnxParser(network, logger)

    # Parse ONNX
    with open(onnx_path, "rb") as f:
        if not parser.parse(f.read()):
            for i in range(parser.num_errors):
                print(f"  ERROR: {parser.get_error(i)}")
            return False

    # Config
    config = builder.create_builder_config()
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, WORKSPACE_GB << 30)
    config.set_flag(trt.BuilderFlag.FP16)
    config.builder_optimization_level = OPTIMIZATION_LEVEL

    # Timing cache (tùy chọn, ít ảnh hưởng với opt_level=1)
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as f:
            cache_data = f.read()
        cache = config.create_timing_cache(cache_data)
        config.set_timing_cache(cache, ignore_mismatch=True)
        print(f"  Timing cache: {len(cache_data) / 1024:.0f} KB")

    # Build
    print(f"  Building engine (est ~30-40s)...")
    t0 = time.time()
    engine = builder.build_serialized_network(network, config)
    elapsed = time.time() - t0

    if engine is None:
        print("  BUILD FAILED!")
        return False

    # Save engine
    with open(engine_path, "wb") as f:
        f.write(engine)

    # Save timing cache
    try:
        cache = config.get_timing_cache()
        with open(CACHE_FILE, "wb") as f:
            f.write(cache.serialize())
    except:
        pass

    size = os.path.getsize(engine_path) / 1024 / 1024
    print(f"  -> {engine_path} ({size:.1f} MB) [{elapsed:.1f}s ({elapsed/60:.1f} phút)]")
    return True


def convert(pt_path):
    """Pipeline: PT → ONNX → Engine"""
    if not os.path.exists(pt_path):
        print(f"ERROR: Không tìm thấy {pt_path}")
        return False

    print("=" * 60)
    print(f" CONVERT: {pt_path} → TensorRT Engine (FP16)")
    print(f" opt_level={OPTIMIZATION_LEVEL} | workspace={WORKSPACE_GB}GB")
    print("=" * 60)

    t_start = time.time()

    # Bước 1: PT → ONNX
    onnx_path = export_onnx(pt_path)

    # Bước 2: ONNX → Engine
    engine_path = pt_path.replace(".pt", ".engine")
    ok = build_engine(onnx_path, engine_path)

    t_total = time.time() - t_start

    print("")
    if ok:
        print(f"DONE: {engine_path} [{t_total:.1f}s ({t_total/60:.1f} phút)]")
    else:
        print("FAILED!")

    return ok


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 convert.py <model.pt>")
        print("  VD: python3 convert.py models/yolov8n.pt")
        print("      python3 convert.py runs/detect/train/weights/best.pt")
        sys.exit(1)

    convert(sys.argv[1])
