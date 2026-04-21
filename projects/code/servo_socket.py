from src.modules.library.functions.ai_blocks import Close_Camera
from src.modules.library.functions.ai_blocks import Update_Dashboard
from src.modules.library.functions.ai_blocks import Draw_Detections_MultiClass
from src.modules.library.functions.ai_blocks import Run_ONNX_Model
from src.modules.library.functions.ai_blocks import Load_ONNX_Model
from src.modules.library.functions.ai_blocks import Get_Camera_Frame
from src.modules.library.functions.ai_blocks import Init_Camera
# ============================================================
# Import Libraries
# ============================================================
import cv2
import numpy as np

# ============================================================
# Setup (runs once)
# ============================================================
# Step 1: Open the camera (Init_Camera)
capture_camera = Init_Camera()

# Step 2: Load your trained AI model (Load_Engine_Model)
model_session = Load_ONNX_Model(model_path = 'projects/model/servo_socket_20eps_size320.onnx')

# Step 3: Define the detection class name (CLASSES = ["class1", "class2", "class3"])
CLASSES = ["servo", "socket"]

print("[OK] Ready! Starting detection loop...")
while True:
    # ========================================================
    # Main Loop (runs every frame)
    # ========================================================
    # Step 4: Get a camera frame (Get_Camera_Frame)
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Step 5: Run AI detection on frame (Run_Engine_Model)
    predictions = Run_ONNX_Model(model_session = model_session, camera_frame = camera_frame, img_size = '320')

    # Step 6: Draw boxes on detected objects (Draw_Engine_Detections)
    total_objects = Draw_Detections_MultiClass(camera_frame = camera_frame, outputs = predictions, classes = CLASSES, conf_threshold = '0.50')

    # Step 7: Show results on Dashboard (Update_Dashboard)
    Update_Dashboard(camera_frame = camera_frame, var_name = 'Objects', var_value = total_objects)

    # [ENDLOOP]


# Shut down camera and close windows (Close_Camera)
Close_Camera(capture_camera = capture_camera)
