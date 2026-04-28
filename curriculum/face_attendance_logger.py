# TITLE: Face Attendance Logger
# TITLE_VI: Nhật Ký Điểm Danh Khuôn Mặt
# LEVEL: Advanced
# ICON: 📋
# COLOR: #f97316
# DESC: Log attendance when faces are detected.
# DESC_VI: Ghi nhật ký điểm danh khi phát hiện khuôn mặt.
# ORDER: 36
# ============================================================



import ai_vision
import camera
import drawing
import display
import image
import logic
import variables

# Step 1: Load the AI face detection model
detector = ai_vision.Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Create an attendance counter
attendance_count = variables.Create_Number(value = 0)

# Step 3: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Face Attendance Logger running!")

# Step 4: Detect faces and log attendance events
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # AI decision: detect faces in the frame
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)
    face_count = drawing.Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # AI logic: if a face is detected, log the attendance
    if face_count > 0:
        attendance_count = attendance_count + 1
        logic.Print_Message(message = f"Attendance logged! Entry #{attendance_count} — {face_count} face(s)")
        # Cooldown to avoid logging the same person repeatedly
        logic.Wait_Seconds(seconds = 3)

    # Overlay the running attendance count on the frame
    camera_frame = image.draw_text(input_image = camera_frame, text = f'Attendance: {attendance_count}', x = 10, y = 60)

    # Stream the feed and track attendance
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Attendance Count', var_value = attendance_count)

camera.Close_Camera(capture_camera = capture_camera)
