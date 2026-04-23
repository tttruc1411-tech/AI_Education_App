# TITLE: Object Counter with Alert
# TITLE_VI: Đếm Vật Thể Với Cảnh Báo
# LEVEL: Intermediate
# ICON: 🔔
# COLOR: #eab308
# DESC: Detect objects and trigger alerts.
# DESC_VI: Phát hiện vật thể và kích hoạt cảnh báo.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import AI object detection blocks
from src.modules.library.functions.ai_blocks import Load_ONNX_Model, Run_ONNX_Model, Draw_Detections_MultiClass
# Import display blocks
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable
# Import variable block for threshold
from src.modules.library.functions.variables import Create_Number
# Import logic block for alert
from src.modules.library.functions.logic_blocks import Print_Message

# Step 1: Define the object classes to detect (short COCO subset)
classes = ["person", "car", "dog", "cat", "bottle"]

# Step 2: Load the AI object detection model
session = Load_ONNX_Model(model_path = 'projects/model/yolov10n.onnx')

# Step 3: Set an alert threshold
threshold = Create_Number(value = 3)

# Step 4: Start the camera
capture_camera = Init_Camera()
print("[OK] Object Counter ready!")

# Step 5: Detect objects and alert when count exceeds threshold
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Run AI inference on the frame
    outputs = Run_ONNX_Model(model_session = session, camera_frame = camera_frame, img_size = 640)

    # Draw bounding boxes and get the total object count
    count = Draw_Detections_MultiClass(camera_frame = camera_frame, outputs = outputs, classes = classes, conf_threshold = 0.50)

    # Alert if too many objects detected
    if count > threshold:
        Print_Message(message = f"ALERT: {count} objects detected!")

    # Stream the frame and track the count
    Show_Image(camera_frame = camera_frame)
    Observe_Variable(var_name = 'Objects Found', var_value = count)

Close_Camera(capture_camera = capture_camera)
