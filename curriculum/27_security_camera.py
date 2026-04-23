# TITLE: Security Camera
# TITLE_VI: Camera An Ninh
# LEVEL: Advanced
# ICON: 🔒
# COLOR: #f97316
# DESC: Build an AI-powered security system.
# DESC_VI: Xây dựng hệ thống an ninh sử dụng AI.
# ============================================================

# Import camera blocks (Camera category)
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import AI object detection blocks (AI Vision category)
from src.modules.library.functions.ai_blocks import Load_ONNX_Model, Run_ONNX_Model, Draw_Detections_MultiClass
# Import image processing for text overlay (Image Processing category)
from src.modules.library.functions.image_processing import draw_text
# Import display blocks (Display category)
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable, Show_FPS
# Import logic blocks (Logic category)
from src.modules.library.functions.logic_blocks import Print_Message

# Step 1: Define target classes — AI will scan for these objects
classes = ["person", "car", "dog", "cat", "bicycle"]

# Step 2: Load the ONNX object detection model
session = Load_ONNX_Model(model_path = 'projects/model/yolov10n.onnx')

# Step 3: Start the camera
capture_camera = Init_Camera()
print("[OK] Security Camera system active!")

# Step 4: Monitor the feed — alert when a person is detected
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # AI decision: run object detection on every frame
    outputs = Run_ONNX_Model(model_session = session, camera_frame = camera_frame, img_size = 640)

    # Draw bounding boxes; conf_threshold filters low-confidence detections
    count = Draw_Detections_MultiClass(camera_frame = camera_frame, outputs = outputs, classes = classes, conf_threshold = 0.50)

    # AI logic: check if any "person" was detected in the results
    # If objects found, overlay a red ALERT warning on the frame
    if count > 0:
        camera_frame = draw_text(input_image = camera_frame, text = 'ALERT: Motion Detected!', x = 10, y = 60)
        Print_Message(message = f"SECURITY ALERT: {count} object(s) detected!")
    else:
        # No threats — display all-clear status
        camera_frame = draw_text(input_image = camera_frame, text = 'Status: All Clear', x = 10, y = 60)

    # Overlay FPS to monitor system performance
    camera_frame = Show_FPS(camera_frame = camera_frame)

    # Stream the annotated feed and track detection count
    Show_Image(camera_frame = camera_frame)
    Observe_Variable(var_name = 'Threats', var_value = count)

Close_Camera(capture_camera = capture_camera)
