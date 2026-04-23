# TITLE: Smart Doorbell
# TITLE_VI: Chuông Cửa Thông Minh
# LEVEL: Advanced
# ICON: 🔔
# COLOR: #f97316
# DESC: Build a smart doorbell that detects visitors.
# DESC_VI: Xây dựng chuông cửa thông minh phát hiện khách.
# ============================================================

# Import camera blocks (Camera category)
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera, Save_Frame
# Import AI face detection blocks (AI Vision category)
from src.modules.library.functions.ai_blocks import Load_YuNet_Model, Run_YuNet_Model, Draw_Detections
# Import image processing for overlays (Image Processing category)
from src.modules.library.functions.image_processing import draw_text
# Import display blocks (Display category)
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable, Draw_Rectangle
# Import logic blocks (Logic category)
from src.modules.library.functions.logic_blocks import Print_Message, Wait_Seconds

# Step 1: Load the AI face detection model
detector = Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera
capture_camera = Init_Camera()
visitor_count = 0
print("[OK] Smart Doorbell active — watching for visitors!")

# Step 3: Monitor for visitors and ring the doorbell
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # AI decision: detect faces to identify visitors
    Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)
    face_count = Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Visitor')

    # AI logic: if a face is detected, ring the doorbell
    if face_count > 0:
        # Draw a green notification banner at the top
        camera_frame = Draw_Rectangle(camera_frame = camera_frame, x = 0, y = 0, width = 640, height = 50, color = 'green')
        camera_frame = draw_text(input_image = camera_frame, text = 'Welcome! Visitor detected!', x = 140, y = 35)
        # Simulate doorbell ring
        Print_Message(message = "Ding dong! A visitor is at the door!")
        # Save a snapshot of the visitor
        visitor_count = visitor_count + 1
        Save_Frame(camera_frame = camera_frame, file_path = f'visitor_{visitor_count}.jpg')
        # Cooldown to avoid repeated rings for the same visitor
        Wait_Seconds(seconds = 5)
    else:
        # No visitor — show idle status
        camera_frame = draw_text(input_image = camera_frame, text = 'Monitoring...', x = 10, y = 30)

    # Stream the feed and track visitor count
    Show_Image(camera_frame = camera_frame)
    Observe_Variable(var_name = 'Visitors', var_value = visitor_count)

Close_Camera(capture_camera = capture_camera)
