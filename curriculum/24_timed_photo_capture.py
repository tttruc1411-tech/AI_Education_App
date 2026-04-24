# TITLE: Timed Photo Capture
# TITLE_VI: Chụp Ảnh Hẹn Giờ
# LEVEL: Intermediate
# ICON: ⏱️
# COLOR: #eab308
# DESC: Auto-capture photos when faces appear.
# DESC_VI: Tự động chụp ảnh khi phát hiện khuôn mặt.
# ============================================================



import ai_vision
import camera
import drawing
import display
import logic

# Step 1: Load the AI face detection model
detector = ai_vision.Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Timed Photo Capture ready!")

# Step 3: Detect faces and capture photos with a countdown
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Run AI face detection
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)
    face_count = drawing.Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # Show the live feed
    display.Show_Image(camera_frame = camera_frame)

    # If a face is detected, wait and then save the photo
    if face_count > 0:
        print("Face detected! Capturing in 3 seconds...")
        logic.Wait_Seconds(seconds = 3)
        camera.Save_Frame(camera_frame = camera_frame, file_path = 'face_capture.jpg')
        print("Photo saved! Waiting before next capture...")
        logic.Wait_Seconds(seconds = 5)

camera.Close_Camera(capture_camera = capture_camera)
