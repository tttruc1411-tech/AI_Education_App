# TITLE: AI Art Filter
# TITLE_VI: Bộ Lọc Nghệ Thuật AI
# LEVEL: Advanced
# ICON: 🎭
# COLOR: #f97316
# DESC: Apply artistic effects when faces are detected.
# DESC_VI: Áp dụng hiệu ứng nghệ thuật khi phát hiện khuôn mặt.
# ORDER: 37
# ============================================================



import ai_vision
import camera
import drawing
import display
import image
import logic

# Step 1: Load the AI face detection model
detector = ai_vision.Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] AI Art Filter ready! Show your face for art mode!")

# Step 3: Apply artistic effects only when a face is detected
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # AI decision: detect faces to trigger the art filter
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)
    face_count = drawing.Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # AI logic: if face detected, apply the full artistic effect chain
    if face_count > 0:
        # Art pipeline: grayscale → edge detection → brighten → mirror flip
        camera_frame = image.convert_to_gray(input_image = camera_frame)
        camera_frame = image.detect_edges(input_image = camera_frame, threshold1 = 80, threshold2 = 180)
        camera_frame = image.adjust_brightness(input_image = camera_frame, factor = 1.5)
        camera_frame = image.flip_image(input_image = camera_frame, direction = 'horizontal')
        logic.Print_Message(message = "Art mode activated!")
    else:
        # No face — show the normal unfiltered camera feed
        logic.Print_Message(message = "Normal mode — no face detected")

    # Stream the result and show current mode
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Art Mode', var_value = face_count > 0)

camera.Close_Camera(capture_camera = capture_camera)
