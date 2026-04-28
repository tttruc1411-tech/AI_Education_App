# TITLE: Multi-Model Speed Comparison
# TITLE_VI: So Sánh Tốc Độ Nhiều Mô Hình AI
# LEVEL: Advanced
# ICON: 🏎️
# COLOR: #f97316
# DESC: Compare AI model speeds side by side.
# DESC_VI: So sánh tốc độ các mô hình AI cạnh nhau.
# ORDER: 31
# ============================================================



import ai_vision
import camera
import drawing
import display
import variables

# Step 1: Load BOTH AI models for comparison
# Model A: YuNet — lightweight face detection
face_detector = ai_vision.Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')
# Model B: YOLOv10 — heavier multi-class object detection
object_session = ai_vision.Load_ONNX_Model(model_path = 'projects/model/yolov10n.onnx')
classes = ["person", "car", "dog", "cat", "bottle"]

# Step 2: Create counters to track total inferences per model
yunet_count = variables.Create_Number(value = 0)
onnx_count = variables.Create_Number(value = 0)

# Step 3: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Multi-Model Speed Comparison running!")

# Step 4: Run both models on the same frame and compare
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # --- Model A: YuNet face detection ---
    ai_vision.Run_YuNet_Model(ai_detector = face_detector, camera_frame = camera_frame)
    _, faces = face_detector.detect(camera_frame)
    face_count = drawing.Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')
    yunet_count = yunet_count + 1

    # --- Model B: ONNX object detection on the SAME frame ---
    outputs = ai_vision.Run_ONNX_Model(model_session = object_session, camera_frame = camera_frame, img_size = 640)
    obj_count = drawing.Draw_Detections_MultiClass(camera_frame = camera_frame, outputs = outputs, classes = classes, conf_threshold = 0.50)
    onnx_count = onnx_count + 1

    # Overlay FPS — shows combined processing speed of both models
    camera_frame = display.Show_FPS(camera_frame = camera_frame)

    # Stream the combined result and track inference counts
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'YuNet Inferences', var_value = yunet_count)
    display.Observe_Variable(var_name = 'ONNX Inferences', var_value = onnx_count)

camera.Close_Camera(capture_camera = capture_camera)
