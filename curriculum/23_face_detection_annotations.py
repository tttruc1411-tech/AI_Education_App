# TITLE: Face Detection with Annotations
# TITLE_VI: Nhận Diện Khuôn Mặt Với Chú Thích
# LEVEL: Intermediate
# ICON: 🏷️
# COLOR: #eab308
# DESC: Add custom labels to face detection.
# DESC_VI: Thêm nhãn tùy chỉnh vào nhận diện khuôn mặt.
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
print("[OK] Face Detection with Annotations ready!")

# Step 3: Detect faces and add custom annotations
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Run AI face detection
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)

    # Draw detection boxes around faces
    face_count = drawing.Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # Draw a status bar at the top of the frame
    camera_frame = display.Draw_Rectangle(camera_frame = camera_frame, x = 0, y = 0, width = 640, height = 40, color = 'blue')

    # Overlay the face count as a custom label on the status bar
    camera_frame = image.draw_text(input_image = camera_frame, text = f'Faces: {face_count}', x = 10, y = 28)

    # Stream the annotated frame and track the count
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Face Count', var_value = face_count)

camera.Close_Camera(capture_camera = capture_camera)
