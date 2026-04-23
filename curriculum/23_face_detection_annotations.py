# TITLE: Face Detection with Annotations
# TITLE_VI: Nhận Diện Khuôn Mặt Với Chú Thích
# LEVEL: Intermediate
# ICON: 🏷️
# COLOR: #eab308
# DESC: Add custom labels to face detection.
# DESC_VI: Thêm nhãn tùy chỉnh vào nhận diện khuôn mặt.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import AI face detection blocks
from src.modules.library.functions.ai_blocks import Load_YuNet_Model, Run_YuNet_Model, Draw_Detections
# Import image processing for text overlay
from src.modules.library.functions.image_processing import draw_text
# Import display blocks
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable, Draw_Rectangle

# Step 1: Load the AI face detection model
detector = Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera
capture_camera = Init_Camera()
print("[OK] Face Detection with Annotations ready!")

# Step 3: Detect faces and add custom annotations
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Run AI face detection
    Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)

    # Draw detection boxes around faces
    face_count = Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # Draw a status bar at the top of the frame
    camera_frame = Draw_Rectangle(camera_frame = camera_frame, x = 0, y = 0, width = 640, height = 40, color = 'blue')

    # Overlay the face count as a custom label on the status bar
    camera_frame = draw_text(input_image = camera_frame, text = f'Faces: {face_count}', x = 10, y = 28)

    # Stream the annotated frame and track the count
    Show_Image(camera_frame = camera_frame)
    Observe_Variable(var_name = 'Face Count', var_value = face_count)

Close_Camera(capture_camera = capture_camera)
