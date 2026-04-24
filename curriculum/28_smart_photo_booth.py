# TITLE: Smart Photo Booth
# TITLE_VI: Quầy Chụp Ảnh Thông Minh
# LEVEL: Advanced
# ICON: 📸
# COLOR: #f97316
# DESC: Auto-capture stylized photos when faces appear.
# DESC_VI: Tự động chụp ảnh nghệ thuật khi phát hiện khuôn mặt.
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
photo_number = 0
print("[OK] Smart Photo Booth ready! Smile for the camera!")

# Step 3: Detect faces and auto-capture stylized photos
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # AI decision: detect faces in the current frame
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)
    face_count = drawing.Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # AI logic: if a face is found, apply effects and capture
    if face_count > 0:
        # Brighten the frame for a flattering photo effect
        camera_frame = image.adjust_brightness(input_image = camera_frame, factor = 1.3)
        # Draw a decorative border frame around the photo
        camera_frame = display.Draw_Rectangle(camera_frame = camera_frame, x = 5, y = 5, width = 630, height = 470, color = 'yellow')
        # Add a fun label overlay
        camera_frame = image.draw_text(input_image = camera_frame, text = 'Say Cheese!', x = 200, y = 460)
        # Save the stylized snapshot
        photo_number = photo_number + 1
        camera.Save_Frame(camera_frame = camera_frame, file_path = f'booth_photo_{photo_number}.jpg')
        # Cooldown to avoid rapid-fire captures
        logic.Wait_Seconds(seconds = 3)
    else:
        # No face — prompt the user to step in front of the camera
        camera_frame = image.draw_text(input_image = camera_frame, text = 'Step in for a photo!', x = 150, y = 240)

    # Stream the live feed and track photo count
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Photos Taken', var_value = photo_number)

camera.Close_Camera(capture_camera = capture_camera)
