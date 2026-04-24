# TITLE: Object Counter with Alert
# TITLE_VI: Đếm Vật Thể Với Cảnh Báo
# LEVEL: Intermediate
# ICON: 🔔
# COLOR: #eab308
# DESC: Detect objects and trigger alerts.
# DESC_VI: Phát hiện vật thể và kích hoạt cảnh báo.
# ============================================================



import ai_vision
import camera
import drawing
import display
import logic
import variables

# Step 1: Define the object classes to detect (short COCO subset)
classes = ["person", "car", "dog", "cat", "bottle"]

# Step 2: Load the AI object detection model
session = ai_vision.Load_ONNX_Model(model_path = 'projects/model/yolov10n.onnx')

# Step 3: Set an alert threshold
threshold = variables.Create_Number(value = 3)

# Step 4: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Object Counter ready!")

# Step 5: Detect objects and alert when count exceeds threshold
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Run AI inference on the frame
    outputs = ai_vision.Run_ONNX_Model(model_session = session, camera_frame = camera_frame, img_size = 640)

    # Draw bounding boxes and get the total object count
    count = drawing.Draw_Detections_MultiClass(camera_frame = camera_frame, outputs = outputs, classes = classes, conf_threshold = 0.50)

    # Alert if too many objects detected
    if count > threshold:
        logic.Print_Message(message = f"ALERT: {count} objects detected!")

    # Stream the frame and track the count
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Objects Found', var_value = count)

camera.Close_Camera(capture_camera = capture_camera)
