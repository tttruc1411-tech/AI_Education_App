# TITLE: Face-Triggered Filter
# TITLE_VI: Bộ Lọc Kích Hoạt Bằng Khuôn Mặt
# LEVEL: Intermediate
# ICON: 👤
# COLOR: #eab308
# DESC: Apply filters only when a face is detected.
# DESC_VI: Áp dụng bộ lọc chỉ khi phát hiện khuôn mặt.
# ============================================================



import ai_vision
import camera
import drawing
import display
import image

# Step 1: Load the AI face detection model
detector = ai_vision.Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Face-Triggered Filter ready!")

# Step 3: Apply filters based on face detection
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Run AI face detection on the frame
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)
    face_count = drawing.Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # If a face is detected, apply grayscale + blur filters
    if face_count > 0:
        camera_frame = image.convert_to_gray(input_image = camera_frame)
        camera_frame = image.apply_blur(input_image = camera_frame, kernel_size = 15)
    else:
        # No face detected — show the normal camera feed
        pass

    # Stream the result and track face status
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Face Detected', var_value = face_count > 0)

camera.Close_Camera(capture_camera = capture_camera)
