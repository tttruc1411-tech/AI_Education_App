import tensorrt as trt
import sys
import os
import time

# ======================== CONFIG ========================
# YuNet specific settings
WORKSPACE_GB = 1         # Safe for 8GB Orin Nano
OPTIMIZATION_LEVEL = 3   # YuNet is small, level 3 is fast enough to build
# ========================================================

def build_engine(onnx_path, engine_path):
    """ONNX → TensorRT Engine (FP16)"""
    print(f"[*] Converting: {onnx_path} → {engine_path}")
    print(f"[*] Config: FP16=True, Workspace={WORKSPACE_GB}GB, OptLevel={OPTIMIZATION_LEVEL}")

    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    
    # Define Network
    network = builder.create_network(
        1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
    )
    parser = trt.OnnxParser(network, logger)

    # Parse ONNX
    if not os.path.exists(onnx_path):
        print(f"ERROR: File {onnx_path} not found.")
        return False

    with open(onnx_path, "rb") as f:
        if not parser.parse(f.read()):
            for i in range(parser.num_errors):
                print(f"  PARSE ERROR: {parser.get_error(i)}")
            return False

    # Builder Config
    config = builder.create_builder_config()
    
    # Set Workspace (Modern TRT API uses set_memory_pool_limit)
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, WORKSPACE_GB << 30)
    
    # Enable FP16 (Crucial for Jetson performance)
    if builder.platform_has_tf32:
        config.set_flag(trt.BuilderFlag.TF32)
    if builder.platform_has_fast_fp16:
        config.set_flag(trt.BuilderFlag.FP16)
    
    config.builder_optimization_level = OPTIMIZATION_LEVEL

    # Build Engine
    print(f"[*] Building engine... This may take a moment.")
    t0 = time.time()
    serialized_engine = builder.build_serialized_network(network, config)
    elapsed = time.time() - t0

    if serialized_engine is None:
        print("  BUILD FAILED!")
        return False

    # Save Engine
    with open(engine_path, "wb") as f:
        f.write(serialized_engine)

    size = os.path.getsize(engine_path) / 1024 / 1024
    print(f"[*] Success! Saved to: {engine_path} ({size:.1f} MB)")
    print(f"[*] Build time: {elapsed:.1f}s")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 convert_yunet.py <model.onnx>")
        print("Example: python3 convert_yunet.py face_detection_yunet_2023mar.onnx")
        sys.exit(1)

    input_onnx = sys.argv[1]
    output_engine = input_onnx.replace(".onnx", ".engine")
    
    build_engine(input_onnx, output_engine)


