import sys
import os
import base64

# Suppress noisy C-library warnings on Jetson before imports trigger them
os.environ["OPENCV_LOG_LEVEL"] = "SILENT"
os.environ["ORT_LOG_LEVEL"] = "ERROR"

import cv2
import numpy as np

# Temporarily silence fd-level stderr during ORT import to suppress
# the C++ "device_discovery.cc" warning on Jetson (writes to fd 2 directly)
_devnull = os.open(os.devnull, os.O_WRONLY)
_old_stderr = os.dup(2)
os.dup2(_devnull, 2)
import onnxruntime as ort
os.dup2(_old_stderr, 2)
os.close(_devnull)
os.close(_old_stderr)

ort.set_default_logger_severity(3)  # 3 = ERROR only

def Init_Camera(camera_id=0):
    """
    Opens the camera and checks for errors.
    Returns the capture object.
    """
    capture_camera = cv2.VideoCapture(camera_id)
    if not capture_camera.isOpened():
        print(f"ERROR: Could not open camera {camera_id}.")
        print("TIP: Make sure no other app is using the camera.")
        sys.exit()
    return capture_camera

def Get_Camera_Frame(capture_camera):
    """
    Reads a single frame from the camera.
    Returns the frame if successful, or None if the camera can't be read.
    """
    if capture_camera is None:
        return None
    ret, camera_frame = capture_camera.read()
    if not ret:
        print("ERROR: Cannot access camera frame.")
        print("TIP: Check if the camera was accidentally disconnected.")
        return None
    return camera_frame

def Close_Camera(capture_camera):
    """
    Successfully releases the camera and closes any OpenCV windows.
    """
    if capture_camera is not None:
        capture_camera.release()
    cv2.destroyAllWindows()
    print("[OK] Camera released and windows closed.")

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

def Draw_Detections(camera_frame, results, label="Detected"):
    """
    Draws bounding boxes and labels for AI detection results.
    - Face Mode (YuNet): Results as [x, y, w, h, ...] (15 values total)
    - Object Mode (YOLOv10): Results as [x1, y1, x2, y2, confidence, class_id]
    - Simple Mode: [x, y, w, h]
    """
    count = 0
    if results is not None:
        count = len(results)
        for f in results:
            # Different models have different output columns!
            
            # --- INTERMEDIATE MODE: YOLOv10 (Length 6) ---
            if len(f) == 6:
                x1, y1, x2, y2, conf, cls = f[0], f[1], f[2], f[3], f[4], f[5]
                x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
                
                name = label[int(cls)] if isinstance(label, list) else f"{label} {int(cls)}"
                display_text = f"{name} ({conf*100:.0f}%)"
            
            # --- BEGINNER MODE: Face Detection (YuNet has 15 columns) ---
            elif len(f) == 15:
                # YuNet format: [x, y, w, h, lx1, ly1, ... conf]
                x, y, w, h = map(int, f[0:4])
                conf = f[14]
                display_text = f"{label} ({conf*100:.0f}%)" if label else f"Face ({conf*100:.0f}%)"
            
            # --- BASIC MODE: Simple Boxes (Length 4) ---
            else:
                x, y, w, h = map(int, f[:4])
                display_text = label
            
            # 1. Draw Bounding Box
            cv2.rectangle(camera_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 2. Draw Label Background
            (tw, th), _ = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            cv2.rectangle(camera_frame, (x, y - th - 10), (x + tw, y), (0, 255, 0), -1)
            
            # 3. Draw Text (Solid Black for maximum contrast)
            cv2.putText(camera_frame, display_text, (x, y - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    return count

def Update_Dashboard(camera_frame, var_name=None, var_value=None):
    """
    Sends the frame to the Live Feed and optionally updates a variable in the Results panel.
    """
    # 1. Update Variable if provided
    if var_name is not None:
        print(f"VAR:{var_name}:{var_value}")
        
    # 2. Stream Frame to UI
    if camera_frame is not None:
        ok, buffer = cv2.imencode('.jpg', camera_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if ok:
            img_b64 = base64.b64encode(buffer).decode('utf-8')
            print(f"IMG:{img_b64}")
        
    # 3. Flush output for real-time performance
    sys.stdout.flush()

def Draw_Detections_MultiClass(camera_frame, outputs, classes, conf_threshold=0.50):
    """
    Advanced block that parses raw YOLO ONNX output, scales coordinates, 
    applies Non-Maximum Suppression (NMS), and draws the results!
    """
    if len(outputs) == 0: return 0
    
    fh, fw, _ = camera_frame.shape 
    detections = outputs[0][0]  # Standard [1, 300, 6] YOLO shape
    
    boxes, confidences, class_ids = [], [], []
    
    for i in range(len(detections)):
        data = detections[i]
        
        # ℹ️ DYNAMIC COLUMN FIX
        if data[4] > 1.0 or data[4].is_integer():
            class_id = int(data[4])
            confidence = float(data[5])
        else:
            confidence = float(data[4])
            class_id = int(data[5])
        
        if confidence > conf_threshold: 
            # 📏 SCALING LOGIC
            if data[2] <= 1.5:  
                x1 = int(data[0] * fw)
                y1 = int(data[1] * fh)
                x2 = int(data[2] * fw)
                y2 = int(data[3] * fh)
            else:               
                x1 = int(data[0] * (fw / 640))
                y1 = int(data[1] * (fh / 640))
                x2 = int(data[2] * (fw / 640))
                y2 = int(data[3] * (fh / 640))
                
            width = x2 - x1
            height = y2 - y1
            
            boxes.append([x1, y1, width, height])
            confidences.append(confidence)
            class_ids.append(class_id)
 
    # Filtering overlapping boxes down to exactly 1 perfect box!
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, 0.4)
    
    count = 0
    if len(indices) > 0:
        for i in indices:
            idx = int(i) if isinstance(i, (int, np.integer)) else i[0]
            
            x, y, width, height = boxes[idx]
            conf = confidences[idx]
            cls_id = class_ids[idx]
            x2, y2 = x + width, y + height
            
            # --- 🏷️ LABELING & DRAWING ---
            name = classes[cls_id] if cls_id < len(classes) else f"ID:{cls_id}"
            display_text = f"{name} ({conf*100:.0f}%)"
            
            cv2.rectangle(camera_frame, (x, y), (x2, y2), (0, 255, 0), 2)
            
            (tw, th), _ = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            cv2.rectangle(camera_frame, (x, y - th - 10), (x + tw, y), (0, 255, 0), -1)
            
            cv2.putText(camera_frame, display_text, (x, y - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)
                        
            count += 1

    return count

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
    if 'TensorrtExecutionProvider' in available:
        providers.append('TensorrtExecutionProvider')
    if 'CUDAExecutionProvider' in available:
        providers.append('CUDAExecutionProvider')
    providers.append('CPUExecutionProvider')

    device = "GPU" if len(providers) > 1 else "CPU"
    print(f"[OK] Loading AI Model using ONNX Runtime ({device})...")
    session = ort.InferenceSession(model_path, providers=providers)
    return session

def Run_ONNX_Model(model_session, camera_frame, img_size=640):
    """
    Prepares a camera frame and runs it through the loaded ONNX session.
    img_size is forced to a square (e.g., 640x640 or 320x320) per YOLO standards.
    """
    if model_session is None or camera_frame is None:
        return []
        
    input_name = model_session.get_inputs()[0].name
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

def Run_Engine_Model(engine_model, camera_frame):
    """
    Runs high-speed inference on a camera frame using the loaded engine model.
    Returns a list of detections: [x1, y1, x2, y2, confidence, class_id]
    """
    if engine_model is None or camera_frame is None:
        return []
        
    results = engine_model(camera_frame, verbose=False)
    
    # Process the first result from the list
    if len(results) > 0 and len(results[0].boxes) > 0:
        # results[0].boxes.data contains [x1, y1, x2, y2, conf, cls] as a tensor
        return results[0].boxes.data.tolist()
        
    return []

def Draw_Engine_Detections(camera_frame, results, classes=None):
    """
    High-fidelity drawing block for .engine model results.
    Returns the number of objects detected.
    """
    # Simply reuse the robust multi-format Draw_Detections block
    return Draw_Detections(camera_frame, results, label=classes if classes else "Object")
