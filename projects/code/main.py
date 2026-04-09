# ============================================================
# Import Libraries
# ============================================================
import cv2
import numpy as np

from src.modules.library.functions.ai_blocks import Update_Dashboard, Draw_Detections_MultiClass, Draw_Engine_Detections, Run_ONNX_Model, Load_ONNX_Model, Get_Camera_Frame, Init_Camera, Close_Camera
# ============================================================
# Setup (runs once)
# ============================================================

# Step 1: Open the camera
capture_camera = Init_Camera()

# Step 2: Load your trained AI model
model_session = Load_ONNX_Model(model_path = 'projects/model/yolov10n.onnx')

# Step 3: Define the detection class name
# Full COCO Labels
CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop",
    "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]


print("[OK] Ready! Starting detection loop...")
while True:
    # ========================================================
    # Main Loop (runs every frame)
    # ========================================================
    # Step 4: Get a camera frame (Get_Camera_Frame)
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Step 5: Run AI detection on frame (Run_Engine_Model)
    predictions = Run_ONNX_Model(model_session = model_session, camera_frame = camera_frame, img_size = 640)

    # Step 6: Draw boxes on detected objects (Draw_Engine_Detections)
    total_objects = Draw_Detections_MultiClass(camera_frame = camera_frame, outputs = predictions, classes = CLASSES, conf_threshold = 0.50)

    # Step 7: Show results on Dashboard (Update_Dashboard)
    Update_Dashboard(camera_frame = camera_frame, var_name = 'Objects detected', var_value = total_objects)


    # [ENDLOOP]


Close_Camera(capture_camera = capture_camera)