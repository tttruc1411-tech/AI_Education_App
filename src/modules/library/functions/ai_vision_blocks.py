# src/modules/library/functions/ai_vision_blocks.py
#
# AI model loading and inference functions.
# Usage: import ai_vision
# Then:  ai_vision.Load_YuNet_Model(), ai_vision.Run_ONNX_Model(), etc.

import os
import cv2
import numpy as np

# Suppress noisy C-library warnings on Jetson before imports trigger them
os.environ["OPENCV_LOG_LEVEL"] = "SILENT"
os.environ["ORT_LOG_LEVEL"] = "ERROR"

import onnxruntime as ort

ort.set_default_logger_severity(3)  # 3 = ERROR only


def Load_YuNet_Model(model_path):
    """
    Loads the YuNet Face Detection model using OpenCV's native detector.
    """
    if not os.path.exists(model_path):
        print(f"ERROR: Model {model_path} not found!")
        return None
    # Initialize with default size, Run_YuNet_Model will auto-scale during loop
    ai_detector = cv2.FaceDetectorYN.create(model_path, "", (320, 320))
    return ai_detector


def Run_YuNet_Model(ai_detector, camera_frame):
    """
    Automatically sets the input size for the AI model based on the frame.
    """
    if camera_frame is None: return
    height, width, _ = camera_frame.shape
    ai_detector.setInputSize((width, height))


def Load_ONNX_Model(model_path):
    """
    Loads an ONNX AI model natively using Microsoft's ONNX Runtime.
    Prefers GPU (TensorRT > CUDA) when available, falls back to CPU.
    """
    if not os.path.exists(model_path):
        print(f"ERROR: Model {model_path} missing! Check your projects/model folder.")
        return None

    available = ort.get_available_providers()
    providers = []
    if 'CUDAExecutionProvider' in available:
        providers.append(('CUDAExecutionProvider', {'device_id': 0}))
    providers.append('CPUExecutionProvider')

    device = "GPU" if 'CUDAExecutionProvider' in available else "CPU"
    print(f"[OK] Loading AI Model using ONNX Runtime ({device})...")

    # Suppress C-level stderr during session creation (CUDA init warnings)
    _dn = os.open(os.devnull, os.O_WRONLY)
    _se = os.dup(2)
    os.dup2(_dn, 2)
    session = ort.InferenceSession(model_path, providers=providers)
    os.dup2(_se, 2)
    os.close(_dn)
    os.close(_se)
    return session


def Run_ONNX_Model(model_session, camera_frame, img_size=640):
    """
    Prepares a camera frame and runs it through the loaded ONNX session.
    img_size is forced to a square (e.g., 640x640 or 320x320) per YOLO standards.
    Auto-detects model input size when possible.
    """
    if model_session is None or camera_frame is None:
        return []

    img_size = int(img_size)
    # Auto-detect model's expected input size to prevent shape mismatch
    model_input = model_session.get_inputs()[0]
    input_name = model_input.name
    input_shape = model_input.shape  # e.g. [1, 3, 320, 320]
    if len(input_shape) == 4 and isinstance(input_shape[2], int) and input_shape[2] in (320, 640):
        img_size = input_shape[2]

    # Pre-processing: Resizes and colors the frame for the AI
    blob = cv2.dnn.blobFromImage(camera_frame, 1/255.0, (img_size, img_size), swapRB=True, crop=False)

    # Run the "Brain"
    outputs = model_session.run(None, {input_name: blob})
    return outputs


def Load_Engine_Model(model_path):
    """
    Loads a TensorRT (.engine) model using the Ultralytics YOLO framework.
    This is optimized for high-speed inference on AI-enabled devices like Jetson.
    """
    if not os.path.exists(model_path):
        print(f"ERROR: Model {model_path} not found!")
        print("TIP: Check the workspace to ensure the file path is correct.")
        return None

    # Proactive check for TensorRT library to provide a student-friendly error
    try:
        import tensorrt
    except ImportError:
        print("ERROR: TensorRT library not found in this environment.")
        print("TIP: .engine models require 'tensorrt' package. Run 'pip install tensorrt' or use a Jetson/GPU environment.")
        return None

    from ultralytics import YOLO
    print(f"[OK] Loading TensorRT Model (.engine)...")
    # task='detect' is explicitly set to ensure consistent output format
    model = YOLO(model_path, task='detect')
    return model


def Run_Engine_Model(engine_model, camera_frame, img_size=640):
    """
    Runs high-speed inference on a camera frame using the loaded engine model.
    img_size must match the size the engine was built with (320 or 640).
    Returns a list of detections: [x1, y1, x2, y2, confidence, class_id]
    """
    if engine_model is None or camera_frame is None:
        return []

    img_size = int(img_size)
    if img_size not in (320, 640):
        print(f"ERROR: img_size must be 320 or 640, got {img_size}")
        print("TIP: Use the same size your model was trained with (check Training Configuration).")
        return []

    results = engine_model(camera_frame, imgsz=img_size, verbose=False)

    # Process the first result from the list
    if len(results) > 0 and len(results[0].boxes) > 0:
        return results[0].boxes.data.tolist()

    return []


def Get_Detection_Count(results):
    """
    Extract the number of detections from AI model results.

    Handles multiple result formats:
    - None → 0
    - numpy array → len(results)
    - tuple (retval, faces) → len(faces) if faces is not None else 0

    Parameters
    ----------
    results : various
        Raw detection results from an AI model.

    Returns
    -------
    int
        The number of detections found.
    """
    try:
        if results is None:
            return 0
        if isinstance(results, np.ndarray):
            return len(results)
        if isinstance(results, tuple):
            # YuNet format: (retval, faces)
            if len(results) >= 2:
                faces = results[1]
                return len(faces) if faces is not None else 0
            return 0
        # List of detections (ONNX/Engine format)
        return len(results)
    except Exception as e:
        print(f"[AI Vision] Error in Get_Detection_Count: {e}")
        return 0


def Crop_Detection(camera_frame, results, index=0):
    """
    Crop a detected object region from the camera frame.

    Extracts the bounding box at the given index from results and returns
    the cropped region. The first 4 values of each detection are x, y, w, h.

    Parameters
    ----------
    camera_frame : ndarray
        The source image to crop from.
    results : array-like
        Detection results where each item has [x, y, w, h, ...].
    index : int
        Which detection to crop (0-based).

    Returns
    -------
    ndarray or None
        The cropped image region, or None if index is out of bounds.
    """
    try:
        if results is None or camera_frame is None:
            return None
        if index >= len(results):
            print(f"[AI Vision] Detection index {index} out of range (only {len(results)} detections found).")
            return None
        det = results[index]
        x, y, w, h = int(det[0]), int(det[1]), int(det[2]), int(det[3])
        # Clamp to frame boundaries
        x = max(0, x)
        y = max(0, y)
        h_frame, w_frame = camera_frame.shape[:2]
        x2 = min(x + w, w_frame)
        y2 = min(y + h, h_frame)
        cropped = camera_frame[y:y2, x:x2]
        return cropped
    except Exception as e:
        print(f"[AI Vision] Error in Crop_Detection: {e}")
        return None
