from src.modules.library.functions.ai_blocks import Update_Dashboard
from src.modules.library.functions.ai_blocks import Draw_Engine_Detections
from src.modules.library.functions.ai_blocks import Run_Engine_Model
from src.modules.library.functions.ai_blocks import Load_Engine_Model
from src.modules.library.functions.ai_blocks import Close_Camera
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
engine_model = Load_Engine_Model(model_path = 'projects/model/servo_socket_20eps_320.engine')
# Step 3: Define the detection class name
classname = ["servo", "socket"]

print("[OK] Ready! Starting detection loop...")
while True:
    # ========================================================
    # Main Loop (runs every frame)
    # ========================================================
    # Step 3: Get a camera frame (Get_Camera_Frame)
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Step 4: Run AI detection on frame (Run_Engine_Model)
    engine_results = Run_Engine_Model(engine_model = engine_model, camera_frame = camera_frame, img_size = 320)

    # Step 5: Draw boxes on detected objects (Draw_Engine_Detections)
    obj_count = Draw_Engine_Detections(camera_frame = camera_frame, results = engine_results, classes = classname, conf_threshold = 0.40)

    # Step 6: Show results on Dashboard (Update_Dashboard)
    Update_Dashboard(camera_frame = camera_frame, var_name = 'Objects', var_value = obj_count)

    # [ENDLOOP]


# Shut down camera and close windows (Close_Camera)
Close_Camera(capture_camera = capture_camera)
