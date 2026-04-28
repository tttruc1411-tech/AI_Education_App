# TITLE: Panoramic Servo Scanner
# TITLE_VI: Quét Servo Toàn Cảnh
# LEVEL: Advanced
# ICON: 📡
# COLOR: #f97316
# DESC: Sweep a servo while detecting faces at each position.
# DESC_VI: Quét servo trong khi phát hiện khuôn mặt tại mỗi vị trí.
# ORDER: 48
# ============================================================



import ai_vision
import camera
import display
import logic
import robotics

# ⚠️ WARNING: This example requires ORC Hub hardware


# Step 1: Load the AI face detection model
detector = ai_vision.Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Panoramic Servo Scanner ready!")

# Step 3: Define the servo sweep range and step size
start_angle = 0
end_angle = 180
step = 15
current_angle = start_angle

# Step 4: Sweep the servo across the range, detecting faces at each position
while True:
    # Move the servo to the current scan position
    robotics.Set_Servo(pin = 'S1', angle = current_angle)

    # Brief pause to let the servo settle before capturing
    logic.Wait_Seconds(seconds = 0.3)

    # Capture a frame at this servo position
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Run AI face detection on the current frame
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    retval, faces = detector.detect(camera_frame)

    # Count faces detected at this angle
    face_count = ai_vision.Get_Detection_Count(results = faces)

    # Log results when faces are found at this position
    if face_count > 0:
        timestamp = logic.Get_Timestamp()
        logic.Print_Message(message = f"[{timestamp}] {face_count} face(s) at angle {current_angle}°")

    # Overlay the current scan angle on the frame
    camera_frame = display.Draw_Text_Box(camera_frame = camera_frame, text = f"Angle: {current_angle} deg | Faces: {face_count}", x = 10, y = 10, bg_color = 'blue', text_color = 'white')

    # Stream the feed and track scan progress
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Servo Angle', var_value = current_angle)
    display.Observe_Variable(var_name = 'Faces Found', var_value = face_count)

    # Advance to the next angle; reset to start when sweep is complete
    current_angle = current_angle + step
    if current_angle > end_angle:
        current_angle = start_angle
        logic.Print_Message(message = "Sweep complete — restarting scan...")

camera.Close_Camera(capture_camera = capture_camera)
