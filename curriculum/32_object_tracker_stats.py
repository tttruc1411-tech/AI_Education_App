# TITLE: Object Tracker with Statistics
# TITLE_VI: Theo Dõi Vật Thể Với Thống Kê
# LEVEL: Advanced
# ICON: 📊
# COLOR: #f97316
# DESC: Track objects and display running statistics.
# DESC_VI: Theo dõi vật thể và hiển thị thống kê liên tục.
# ============================================================



import ai_vision
import camera
import drawing
import display
import image
import logic
import variables

# Step 1: Define detection classes
classes = ["person", "car", "dog", "cat", "bottle", "chair"]

# Step 2: Load the AI model
session = ai_vision.Load_ONNX_Model(model_path = 'projects/model/yolov10n.onnx')

# Step 3: Create cumulative tracking variables
total_detections = variables.Create_Number(value = 0)
frame_number = variables.Create_Number(value = 0)

# Step 4: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Object Tracker with Statistics running!")

# Step 5: Detect, track, and display running statistics
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    frame_number = frame_number + 1

    # AI decision: detect objects in the current frame
    outputs = ai_vision.Run_ONNX_Model(model_session = session, camera_frame = camera_frame, img_size = 640)
    count = drawing.Draw_Detections_MultiClass(camera_frame = camera_frame, outputs = outputs, classes = classes, conf_threshold = 0.50)

    # Accumulate total detections across all frames
    total_detections = total_detections + count

    # AI logic: alert when current frame has high activity
    if count > 5:
        logic.Print_Message(message = f"High activity! {count} objects in frame {frame_number}")

    # Overlay running statistics on the frame
    camera_frame = image.draw_text(input_image = camera_frame, text = f'Current: {count}', x = 10, y = 60)
    camera_frame = image.draw_text(input_image = camera_frame, text = f'Total: {total_detections}', x = 10, y = 90)

    # Show FPS for performance monitoring
    camera_frame = display.Show_FPS(camera_frame = camera_frame)

    # Stream the annotated feed and track stats
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Current Count', var_value = count)
    display.Observe_Variable(var_name = 'Total Detections', var_value = total_detections)

camera.Close_Camera(capture_camera = capture_camera)
