# TITLE: Smart Face Counter
# TITLE_VI: Đếm Khuôn Mặt Thông Minh
# LEVEL: Intermediate
# ICON: 🧮
# COLOR: #eab308
# DESC: Count faces with AI and get alerts.
# DESC_VI: Đếm khuôn mặt bằng AI và nhận cảnh báo.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import AI face detection blocks
from src.modules.library.functions.ai_blocks import Load_YuNet_Model, Run_YuNet_Model, Draw_Detections
# Import display blocks
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable, Show_FPS
# Import variable block for threshold
from src.modules.library.functions.variables import Create_Number
# Import logic block for alert message
from src.modules.library.functions.logic_blocks import Print_Message

# Step 1: Load the AI face detection model
detector = Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Set a face count threshold for alerts
threshold = Create_Number(value = 2)

# Step 3: Start the camera
capture_camera = Init_Camera()
print("[OK] Smart Face Counter ready!")

# Step 4: Detect faces in a loop
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Prepare the AI model for this frame size
    Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)

    # Draw boxes around detected faces and get the count
    face_count = Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # Alert if face count exceeds threshold
    if face_count > threshold:
        Print_Message(message = f"ALERT: {face_count} faces detected!")

    # Overlay FPS counter on the frame
    camera_frame = Show_FPS(camera_frame = camera_frame)

    # Stream the frame and track the face count
    Show_Image(camera_frame = camera_frame)
    Observe_Variable(var_name = 'Faces Found', var_value = face_count)

Close_Camera(capture_camera = capture_camera)
