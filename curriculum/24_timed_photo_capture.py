# TITLE: Timed Photo Capture
# TITLE_VI: Chụp Ảnh Hẹn Giờ
# LEVEL: Intermediate
# ICON: ⏱️
# COLOR: #eab308
# DESC: Auto-capture photos when faces appear.
# DESC_VI: Tự động chụp ảnh khi phát hiện khuôn mặt.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera, Save_Frame
# Import AI face detection blocks
from src.modules.library.functions.ai_blocks import Load_YuNet_Model, Run_YuNet_Model, Draw_Detections
# Import display blocks
from src.modules.library.functions.display_blocks import Show_Image
# Import logic blocks for delay
from src.modules.library.functions.logic_blocks import Wait_Seconds

# Step 1: Load the AI face detection model
detector = Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera
capture_camera = Init_Camera()
print("[OK] Timed Photo Capture ready!")

# Step 3: Detect faces and capture photos with a countdown
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Run AI face detection
    Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)
    face_count = Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # Show the live feed
    Show_Image(camera_frame = camera_frame)

    # If a face is detected, wait and then save the photo
    if face_count > 0:
        print("Face detected! Capturing in 3 seconds...")
        Wait_Seconds(seconds = 3)
        Save_Frame(camera_frame = camera_frame, file_path = 'face_capture.jpg')
        print("Photo saved! Waiting before next capture...")
        Wait_Seconds(seconds = 5)

Close_Camera(capture_camera = capture_camera)
