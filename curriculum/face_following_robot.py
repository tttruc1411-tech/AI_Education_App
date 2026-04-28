# TITLE: Face-Following Robot
# TITLE_VI: Robot Theo Dõi Khuôn Mặt
# LEVEL: Advanced
# ICON: 🤖
# COLOR: #f97316
# DESC: Make a robot follow your face.
# DESC_VI: Làm robot theo dõi khuôn mặt của bạn.
# ORDER: 30
# ============================================================

import ai_vision
import camera
import drawing
import display
import logic
import robotics

# ⚠️ WARNING: This example requires ORC Hub hardware (Motor Driver V2) connected via I2C


# Step 1: Load the AI face detection model
detector = ai_vision.Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera — frame width is 640 pixels
capture_camera = camera.Init_Camera()
servo_angle = 90  # Start servo at center position
print("[OK] Face-Following Robot ready!")

# Step 3: Track faces and move the servo to follow
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # AI decision: detect faces in the frame
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)
    face_count = drawing.Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # AI logic: calculate face center and decide servo direction
    if faces is not None and len(faces) > 0:
        # Extract the first detected face bounding box [x, y, w, h, ...]
        face_x = int(faces[0][0])
        face_w = int(faces[0][2])
        face_center_x = face_x + face_w // 2

        # Decision: if face is left of center, pan servo left; otherwise pan right
        frame_center = 320  # Half of 640px frame width
        if face_center_x < frame_center - 50:
            servo_angle = min(servo_angle + 5, 180)  # Pan left
            logic.Print_Message(message = "Panning LEFT to follow face")
        else:
            servo_angle = max(servo_angle - 5, 0)    # Pan right
            logic.Print_Message(message = "Panning RIGHT to follow face")

        # Move the servo to track the face
        robotics.Set_Servo(pin = 'S1', angle = servo_angle)

    # Stream the feed and show current servo angle
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Servo Angle', var_value = servo_angle)

camera.Close_Camera(capture_camera = capture_camera)
