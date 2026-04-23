# TITLE: Face-Triggered Filter
# TITLE_VI: Bộ Lọc Kích Hoạt Bằng Khuôn Mặt
# LEVEL: Intermediate
# ICON: 👤
# COLOR: #eab308
# DESC: Apply filters only when a face is detected.
# DESC_VI: Áp dụng bộ lọc chỉ khi phát hiện khuôn mặt.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import AI face detection blocks
from src.modules.library.functions.ai_blocks import Load_YuNet_Model, Run_YuNet_Model, Draw_Detections
# Import image processing blocks for filters
from src.modules.library.functions.image_processing import convert_to_gray, apply_blur
# Import display blocks
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable

# Step 1: Load the AI face detection model
detector = Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera
capture_camera = Init_Camera()
print("[OK] Face-Triggered Filter ready!")

# Step 3: Apply filters based on face detection
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Run AI face detection on the frame
    Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)
    face_count = Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # If a face is detected, apply grayscale + blur filters
    if face_count > 0:
        camera_frame = convert_to_gray(input_image = camera_frame)
        camera_frame = apply_blur(input_image = camera_frame, kernel_size = 15)
    else:
        # No face detected — show the normal camera feed
        pass

    # Stream the result and track face status
    Show_Image(camera_frame = camera_frame)
    Observe_Variable(var_name = 'Face Detected', var_value = face_count > 0)

Close_Camera(capture_camera = capture_camera)
