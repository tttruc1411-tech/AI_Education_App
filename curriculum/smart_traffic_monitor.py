# TITLE: Smart Traffic Monitor
# TITLE_VI: Giám Sát Giao Thông Thông Minh
# LEVEL: Advanced
# ICON: 🚗
# COLOR: #f97316
# DESC: Count and log detected objects with AI and timestamps.
# DESC_VI: Đếm và ghi nhật ký vật thể phát hiện bằng AI kèm thời gian.
# ORDER: 47
# ============================================================



import ai_vision
import camera
import display
import logic
import variables

# Step 1: Define the traffic-related object classes to detect
classes = ["person", "car", "bus", "truck", "bicycle"]

# Step 2: Load the ONNX object detection model for traffic monitoring
model_session = ai_vision.Load_ONNX_Model(model_path = 'projects/model/yolov10n.onnx')

# Step 3: Start the camera to watch the traffic scene
capture_camera = camera.Init_Camera()
print("[OK] Smart Traffic Monitor active!")

# Step 4: Create a variable to track the total logged events
total_logs = variables.Create_Number(value = 0)

# Step 5: Monitor traffic — detect, count, timestamp, and log
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Run AI object detection on the current frame
    predictions = ai_vision.Run_ONNX_Model(model_session = model_session, camera_frame = camera_frame, img_size = 640)

    # Count how many objects were detected in this frame
    detection_count = ai_vision.Get_Detection_Count(results = predictions)

    # Get the current timestamp for the log entry
    timestamp = logic.Get_Timestamp()

    # Log a message when objects are detected in the scene
    if detection_count > 0:
        logic.Print_Message(message = f"[{timestamp}] Traffic alert: {detection_count} object(s) detected")
        total_logs = total_logs + 1

    # Overlay a status text box on the frame showing live count
    camera_frame = display.Draw_Text_Box(camera_frame = camera_frame, text = f"Objects: {detection_count} | {timestamp}", x = 10, y = 10, bg_color = 'blue', text_color = 'white')

    # Stream the annotated feed and track statistics
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Detections', var_value = detection_count)
    display.Observe_Variable(var_name = 'Total Logs', var_value = total_logs)

camera.Close_Camera(capture_camera = capture_camera)
