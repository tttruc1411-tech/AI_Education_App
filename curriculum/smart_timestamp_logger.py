# TITLE: Smart Timestamp Logger
# TITLE_VI: Nhật Ký Thời Gian Thông Minh
# LEVEL: Intermediate
# ICON: 📝
# COLOR: #eab308
# DESC: Log face detections with timestamps.
# DESC_VI: Ghi nhật ký phát hiện khuôn mặt kèm thời gian.
# ORDER: 44
# ============================================================



import ai_vision
import camera
import display
import logic

# Step 1: Load the AI face detection model
detector = ai_vision.Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Smart Timestamp Logger ready!")

# Step 3: Detect faces, count them, and log with a timestamp
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Run AI face detection on the current frame
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    retval, faces = detector.detect(camera_frame)

    # Count how many faces were detected
    face_count = ai_vision.Get_Detection_Count(results = faces)

    # Get the current timestamp for logging
    timestamp = logic.Get_Timestamp()

    # Log the detection count with the timestamp
    if face_count > 0:
        logic.Print_Message(message = f"[{timestamp}] Detected {face_count} face(s)")

    # Show the camera frame and track the count
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Face Count', var_value = face_count)
    display.Observe_Variable(var_name = 'Last Timestamp', var_value = timestamp)

camera.Close_Camera(capture_camera = capture_camera)
