# TITLE: Security Camera
# TITLE_VI: Camera An Ninh
# LEVEL: Advanced
# ICON: 🔒
# COLOR: #f97316
# DESC: Build an AI-powered security system.
# DESC_VI: Xây dựng hệ thống an ninh sử dụng AI.
# ORDER: 27
# ============================================================



import ai_vision
import camera
import drawing
import display
import image
import logic

# Step 1: Define target classes — AI will scan for these objects
classes = ["person", "car", "dog", "cat", "bicycle"]

# Step 2: Load the ONNX object detection model
session = ai_vision.Load_ONNX_Model(model_path = 'projects/model/yolov10n.onnx')

# Step 3: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Security Camera system active!")

# Step 4: Monitor the feed — alert when a person is detected
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # AI decision: run object detection on every frame
    outputs = ai_vision.Run_ONNX_Model(model_session = session, camera_frame = camera_frame, img_size = 640)

    # Draw bounding boxes; conf_threshold filters low-confidence detections
    count = drawing.Draw_Detections_MultiClass(camera_frame = camera_frame, outputs = outputs, classes = classes, conf_threshold = 0.50)

    # AI logic: check if any "person" was detected in the results
    # If objects found, overlay a red ALERT warning on the frame
    if count > 0:
        camera_frame = image.draw_text(input_image = camera_frame, text = 'ALERT: Motion Detected!', x = 10, y = 60)
        logic.Print_Message(message = f"SECURITY ALERT: {count} object(s) detected!")
    else:
        # No threats — display all-clear status
        camera_frame = image.draw_text(input_image = camera_frame, text = 'Status: All Clear', x = 10, y = 60)

    # Overlay FPS to monitor system performance
    camera_frame = display.Show_FPS(camera_frame = camera_frame)

    # Stream the annotated feed and track detection count
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Threats', var_value = count)

camera.Close_Camera(capture_camera = capture_camera)
