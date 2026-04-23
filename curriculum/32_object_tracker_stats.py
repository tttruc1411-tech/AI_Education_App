# TITLE: Object Tracker with Statistics
# TITLE_VI: Theo Dõi Vật Thể Với Thống Kê
# LEVEL: Advanced
# ICON: 📊
# COLOR: #f97316
# DESC: Track objects and display running statistics.
# DESC_VI: Theo dõi vật thể và hiển thị thống kê liên tục.
# ============================================================

# Import camera blocks (Camera category)
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import AI object detection blocks (AI Vision category)
from src.modules.library.functions.ai_blocks import Load_ONNX_Model, Run_ONNX_Model, Draw_Detections_MultiClass
# Import image processing for stats overlay (Image Processing category)
from src.modules.library.functions.image_processing import draw_text
# Import display blocks (Display category)
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable, Show_FPS
# Import variable blocks for cumulative tracking (Variables category)
from src.modules.library.functions.variables import Create_Number
# Import logic blocks (Logic category)
from src.modules.library.functions.logic_blocks import Print_Message

# Step 1: Define detection classes
classes = ["person", "car", "dog", "cat", "bottle", "chair"]

# Step 2: Load the AI model
session = Load_ONNX_Model(model_path = 'projects/model/yolov10n.onnx')

# Step 3: Create cumulative tracking variables
total_detections = Create_Number(value = 0)
frame_number = Create_Number(value = 0)

# Step 4: Start the camera
capture_camera = Init_Camera()
print("[OK] Object Tracker with Statistics running!")

# Step 5: Detect, track, and display running statistics
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)
    frame_number = frame_number + 1

    # AI decision: detect objects in the current frame
    outputs = Run_ONNX_Model(model_session = session, camera_frame = camera_frame, img_size = 640)
    count = Draw_Detections_MultiClass(camera_frame = camera_frame, outputs = outputs, classes = classes, conf_threshold = 0.50)

    # Accumulate total detections across all frames
    total_detections = total_detections + count

    # AI logic: alert when current frame has high activity
    if count > 5:
        Print_Message(message = f"High activity! {count} objects in frame {frame_number}")

    # Overlay running statistics on the frame
    camera_frame = draw_text(input_image = camera_frame, text = f'Current: {count}', x = 10, y = 60)
    camera_frame = draw_text(input_image = camera_frame, text = f'Total: {total_detections}', x = 10, y = 90)

    # Show FPS for performance monitoring
    camera_frame = Show_FPS(camera_frame = camera_frame)

    # Stream the annotated feed and track stats
    Show_Image(camera_frame = camera_frame)
    Observe_Variable(var_name = 'Current Count', var_value = count)
    Observe_Variable(var_name = 'Total Detections', var_value = total_detections)

Close_Camera(capture_camera = capture_camera)
