# TITLE: Smart Face Counter
# TITLE_VI: Đếm Khuôn Mặt Thông Minh
# LEVEL: Intermediate
# ICON: 🧮
# COLOR: #eab308
# DESC: Count faces with AI and get alerts.
# DESC_VI: Đếm khuôn mặt bằng AI và nhận cảnh báo.
# ============================================================



import ai_vision
import camera
import drawing
import display
import logic
import variables

# Step 1: Load the AI face detection model
detector = ai_vision.Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Set a face count threshold for alerts
threshold = variables.Create_Number(value = 2)

# Step 3: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Smart Face Counter ready!")

# Step 4: Detect faces in a loop
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Prepare the AI model for this frame size
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)

    # Draw boxes around detected faces and get the count
    face_count = drawing.Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # Alert if face count exceeds threshold
    if face_count > threshold:
        logic.Print_Message(message = f"ALERT: {face_count} faces detected!")

    # Overlay FPS counter on the frame
    camera_frame = display.Show_FPS(camera_frame = camera_frame)

    # Stream the frame and track the face count
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Faces Found', var_value = face_count)

camera.Close_Camera(capture_camera = capture_camera)
