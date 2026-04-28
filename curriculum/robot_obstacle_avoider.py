# TITLE: Robot Obstacle Avoider
# TITLE_VI: Robot Tránh Vật Cản
# LEVEL: Advanced
# ICON: 🚗
# COLOR: #f97316
# DESC: Build a robot that avoids obstacles with AI.
# DESC_VI: Xây dựng robot tránh vật cản bằng AI.
# ORDER: 34
# ============================================================

import ai_vision
import camera
import drawing
import display
import logic
import robotics

# ⚠️ WARNING: This example requires ORC Hub hardware (Motor Driver V2) connected via I2C


# Step 1: Define obstacle classes the robot should avoid
classes = ["person", "chair", "bottle", "dog", "cat", "car"]

# Step 2: Load the AI object detection model
session = ai_vision.Load_ONNX_Model(model_path = 'projects/model/yolov10n.onnx')

# Step 3: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Robot Obstacle Avoider ready!")

# Step 4: Drive forward, stop when obstacles are detected
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # AI decision: scan for obstacles in the robot's path
    outputs = ai_vision.Run_ONNX_Model(model_session = session, camera_frame = camera_frame, img_size = 640)
    count = drawing.Draw_Detections_MultiClass(camera_frame = camera_frame, outputs = outputs, classes = classes, conf_threshold = 0.50)

    # AI logic: if obstacles detected, stop; otherwise drive forward
    if count > 0:
        # Obstacle found — emergency stop both motors
        robotics.DC_Stop(pin = 'M1')
        robotics.DC_Stop(pin = 'M2')
        logic.Print_Message(message = f"STOP! {count} obstacle(s) detected!")
    else:
        # Path is clear — drive both motors forward
        robotics.DC_Run(pin = 'M1', speed = 50, time_ms = None)
        robotics.DC_Run(pin = 'M2', speed = 50, time_ms = None)

    # Stream the feed and show obstacle status
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Obstacles', var_value = count)

camera.Close_Camera(capture_camera = capture_camera)
