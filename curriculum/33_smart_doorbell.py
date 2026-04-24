# TITLE: Smart Doorbell
# TITLE_VI: Chuông Cửa Thông Minh
# LEVEL: Advanced
# ICON: 🔔
# COLOR: #f97316
# DESC: Build a smart doorbell that detects visitors.
# DESC_VI: Xây dựng chuông cửa thông minh phát hiện khách.
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
visitor_count = 0
print("[OK] Smart Doorbell active — watching for visitors!")

# Step 3: Monitor for visitors and ring the doorbell
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # AI decision: detect faces to identify visitors
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)
    face_count = drawing.Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Visitor')

    # AI logic: if a face is detected, ring the doorbell
    if face_count > 0:
        # Draw a green notification banner at the top
        camera_frame = display.Draw_Rectangle(camera_frame = camera_frame, x = 0, y = 0, width = 640, height = 50, color = 'green')
        camera_frame = image.draw_text(input_image = camera_frame, text = 'Welcome! Visitor detected!', x = 140, y = 35)
        # Simulate doorbell ring
        logic.Print_Message(message = "Ding dong! A visitor is at the door!")
        # Save a snapshot of the visitor
        visitor_count = visitor_count + 1
        camera.Save_Frame(camera_frame = camera_frame, file_path = f'visitor_{visitor_count}.jpg')
        # Cooldown to avoid repeated rings for the same visitor
        logic.Wait_Seconds(seconds = 5)
    else:
        # No visitor — show idle status
        camera_frame = image.draw_text(input_image = camera_frame, text = 'Monitoring...', x = 10, y = 30)

    # Stream the feed and track visitor count
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Visitors', var_value = visitor_count)

camera.Close_Camera(capture_camera = capture_camera)
