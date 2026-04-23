# TITLE: Face Attendance Logger
# TITLE_VI: Nhật Ký Điểm Danh Khuôn Mặt
# LEVEL: Advanced
# ICON: 📋
# COLOR: #f97316
# DESC: Log attendance when faces are detected.
# DESC_VI: Ghi nhật ký điểm danh khi phát hiện khuôn mặt.
# ============================================================

# Import camera blocks (Camera category)
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import AI face detection blocks (AI Vision category)
from src.modules.library.functions.ai_blocks import Load_YuNet_Model, Run_YuNet_Model, Draw_Detections
# Import image processing for text overlay (Image Processing — draw_text)
from src.modules.library.functions.image_processing import draw_text
# Import display blocks (Display category)
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable
# Import variable blocks for counter (Variables category)
from src.modules.library.functions.variables import Create_Number
# Import logic blocks (Logic category)
from src.modules.library.functions.logic_blocks import Print_Message, Wait_Seconds

# Step 1: Load the AI face detection model
detector = Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Create an attendance counter
attendance_count = Create_Number(value = 0)

# Step 3: Start the camera
capture_camera = Init_Camera()
print("[OK] Face Attendance Logger running!")

# Step 4: Detect faces and log attendance events
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # AI decision: detect faces in the frame
    Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)
    face_count = Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # AI logic: if a face is detected, log the attendance
    if face_count > 0:
        attendance_count = attendance_count + 1
        Print_Message(message = f"Attendance logged! Entry #{attendance_count} — {face_count} face(s)")
        # Cooldown to avoid logging the same person repeatedly
        Wait_Seconds(seconds = 3)

    # Overlay the running attendance count on the frame
    camera_frame = draw_text(input_image = camera_frame, text = f'Attendance: {attendance_count}', x = 10, y = 60)

    # Stream the feed and track attendance
    Show_Image(camera_frame = camera_frame)
    Observe_Variable(var_name = 'Attendance Count', var_value = attendance_count)

Close_Camera(capture_camera = capture_camera)
