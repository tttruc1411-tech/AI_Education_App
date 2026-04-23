# TITLE: Custom Object Detector
# TITLE_VI: Nhận Diện Vật Thể Tùy Chỉnh
# LEVEL: Intermediate
# ICON: 🎯
# COLOR: #eab308
# DESC: Use your own trained AI model.
# DESC_VI: Sử dụng mô hình AI do bạn tự huấn luyện.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import TensorRT engine blocks for custom models
from src.modules.library.functions.ai_blocks import Load_Engine_Model, Run_Engine_Model, Draw_Engine_Detections
# Import display blocks
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable

# NOTE: This example requires a student-trained .engine model file.
# Train your own model using the AI Training tool, then export as .engine

# Step 1: Load your custom-trained TensorRT engine model
engine_model = Load_Engine_Model(model_path = 'projects/model/my_model.engine')

# Step 2: Define your custom class names (from training)
classes = ["my_object"]

# Step 3: Start the camera
capture_camera = Init_Camera()
print("[OK] Custom Object Detector ready!")

# Step 4: Detect objects using your trained model
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Run inference with the custom engine model
    results = Run_Engine_Model(engine_model = engine_model, camera_frame = camera_frame, img_size = 640)

    # Draw bounding boxes for detected objects
    count = Draw_Engine_Detections(camera_frame = camera_frame, results = results, classes = classes, conf_threshold = 0.25)

    # Stream the frame and track detection count
    Show_Image(camera_frame = camera_frame)
    Observe_Variable(var_name = 'Detections', var_value = count)

Close_Camera(capture_camera = capture_camera)
