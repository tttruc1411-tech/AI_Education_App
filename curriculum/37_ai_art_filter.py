# TITLE: AI Art Filter
# TITLE_VI: Bộ Lọc Nghệ Thuật AI
# LEVEL: Advanced
# ICON: 🎭
# COLOR: #f97316
# DESC: Apply artistic effects when faces are detected.
# DESC_VI: Áp dụng hiệu ứng nghệ thuật khi phát hiện khuôn mặt.
# ============================================================

# Import camera blocks (Camera category)
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import AI face detection blocks (AI Vision category)
from src.modules.library.functions.ai_blocks import Load_YuNet_Model, Run_YuNet_Model, Draw_Detections
# Import image processing for artistic effects chain (Image Processing category)
from src.modules.library.functions.image_processing import convert_to_gray, detect_edges, adjust_brightness, flip_image
# Import display blocks (Display category)
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable
# Import logic blocks (Logic category)
from src.modules.library.functions.logic_blocks import Print_Message

# Step 1: Load the AI face detection model
detector = Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera
capture_camera = Init_Camera()
print("[OK] AI Art Filter ready! Show your face for art mode!")

# Step 3: Apply artistic effects only when a face is detected
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # AI decision: detect faces to trigger the art filter
    Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)
    face_count = Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # AI logic: if face detected, apply the full artistic effect chain
    if face_count > 0:
        # Art pipeline: grayscale → edge detection → brighten → mirror flip
        camera_frame = convert_to_gray(input_image = camera_frame)
        camera_frame = detect_edges(input_image = camera_frame, threshold1 = 80, threshold2 = 180)
        camera_frame = adjust_brightness(input_image = camera_frame, factor = 1.5)
        camera_frame = flip_image(input_image = camera_frame, direction = 'horizontal')
        Print_Message(message = "Art mode activated!")
    else:
        # No face — show the normal unfiltered camera feed
        Print_Message(message = "Normal mode — no face detected")

    # Stream the result and show current mode
    Show_Image(camera_frame = camera_frame)
    Observe_Variable(var_name = 'Art Mode', var_value = face_count > 0)

Close_Camera(capture_camera = capture_camera)
