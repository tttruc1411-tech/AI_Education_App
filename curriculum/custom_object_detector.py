# TITLE: Custom Object Detector
# TITLE_VI: Nhận Diện Vật Thể Tùy Chỉnh
# LEVEL: Intermediate
# ICON: 🎯
# COLOR: #eab308
# DESC: Use your own trained AI model.
# DESC_VI: Sử dụng mô hình AI do bạn tự huấn luyện.
# ORDER: 26
# ============================================================



import ai_vision
import camera
import drawing
import display

# NOTE: This example requires a student-trained .engine model file.
# Train your own model using the AI Training tool, then export as .engine

# Step 1: Load your custom-trained TensorRT engine model
engine_model = ai_vision.Load_Engine_Model(model_path = 'projects/model/my_model.engine')

# Step 2: Define your custom class names (from training)
classes = ["my_object"]

# Step 3: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Custom Object Detector ready!")

# Step 4: Detect objects using your trained model
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Run inference with the custom engine model
    results = ai_vision.Run_Engine_Model(engine_model = engine_model, camera_frame = camera_frame, img_size = 640)

    # Draw bounding boxes for detected objects
    count = drawing.Draw_Engine_Detections(camera_frame = camera_frame, results = results, classes = classes, conf_threshold = 0.25)

    # Stream the frame and track detection count
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Detections', var_value = count)

camera.Close_Camera(capture_camera = capture_camera)
