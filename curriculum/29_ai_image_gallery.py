# TITLE: AI Image Gallery
# TITLE_VI: Bộ Sưu Tập Ảnh AI
# LEVEL: Advanced
# ICON: 🖼️
# COLOR: #f97316
# DESC: Create an annotated photo gallery with AI.
# DESC_VI: Tạo bộ sưu tập ảnh được chú thích bằng AI.
# ============================================================



import ai_vision
import camera
import drawing
import display
import image
import logic

# Step 1: Define COCO classes for detection
classes = ["person", "car", "dog", "cat", "bottle", "chair", "cup"]

# Step 2: Load the AI model
session = ai_vision.Load_ONNX_Model(model_path = 'projects/model/yolov10n.onnx')

# Step 3: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] AI Image Gallery — capturing 10 annotated photos!")

# Step 4: Capture a gallery of 10 AI-annotated images
for i in range(10):
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # AI decision: detect objects in the scene
    outputs = ai_vision.Run_ONNX_Model(model_session = session, camera_frame = camera_frame, img_size = 640)

    # Draw bounding boxes on detected objects
    count = drawing.Draw_Detections_MultiClass(camera_frame = camera_frame, outputs = outputs, classes = classes, conf_threshold = 0.50)

    # Annotate the frame with gallery info and detection count
    camera_frame = image.draw_text(input_image = camera_frame, text = f'Gallery #{i + 1} - {count} objects', x = 10, y = 30)

    # Show the annotated frame
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Gallery Photo', var_value = i + 1)

    # Save each annotated frame to build the gallery
    camera.Save_Frame(camera_frame = camera_frame, file_path = f'gallery_{i + 1}.jpg')
    logic.Print_Message(message = f"Saved gallery photo {i + 1}/10 with {count} objects")

    # Brief pause between captures for varied scenes
    logic.Wait_Seconds(seconds = 2)

# Step 5: Clean up
camera.Close_Camera(capture_camera = capture_camera)
print("[OK] Gallery complete! 10 photos saved.")
