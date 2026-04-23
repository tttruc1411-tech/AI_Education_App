# TITLE: Robot Obstacle Avoider
# TITLE_VI: Robot Tránh Vật Cản
# LEVEL: Advanced
# ICON: 🚗
# COLOR: #f97316
# DESC: Build a robot that avoids obstacles with AI.
# DESC_VI: Xây dựng robot tránh vật cản bằng AI.
# ============================================================
# ⚠️ WARNING: This example requires ORC Hub hardware (Motor Driver V2) connected via I2C

# Import camera blocks (Camera category)
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import AI object detection blocks (AI Vision category)
from src.modules.library.functions.ai_blocks import Load_ONNX_Model, Run_ONNX_Model, Draw_Detections_MultiClass
# Import display blocks (Display category)
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable
# Import robotics blocks for motor control (Robotics category)
from src.modules.library.functions.robotics import DC_Run, DC_Stop
# Import logic blocks (Logic category)
from src.modules.library.functions.logic_blocks import Print_Message

# Step 1: Define obstacle classes the robot should avoid
classes = ["person", "chair", "bottle", "dog", "cat", "car"]

# Step 2: Load the AI object detection model
session = Load_ONNX_Model(model_path = 'projects/model/yolov10n.onnx')

# Step 3: Start the camera
capture_camera = Init_Camera()
print("[OK] Robot Obstacle Avoider ready!")

# Step 4: Drive forward, stop when obstacles are detected
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # AI decision: scan for obstacles in the robot's path
    outputs = Run_ONNX_Model(model_session = session, camera_frame = camera_frame, img_size = 640)
    count = Draw_Detections_MultiClass(camera_frame = camera_frame, outputs = outputs, classes = classes, conf_threshold = 0.50)

    # AI logic: if obstacles detected, stop; otherwise drive forward
    if count > 0:
        # Obstacle found — emergency stop both motors
        DC_Stop(pin = 'M1')
        DC_Stop(pin = 'M2')
        Print_Message(message = f"STOP! {count} obstacle(s) detected!")
    else:
        # Path is clear — drive both motors forward
        DC_Run(pin = 'M1', speed = 50, time_ms = None)
        DC_Run(pin = 'M2', speed = 50, time_ms = None)

    # Stream the feed and show obstacle status
    Show_Image(camera_frame = camera_frame)
    Observe_Variable(var_name = 'Obstacles', var_value = count)

Close_Camera(capture_camera = capture_camera)
