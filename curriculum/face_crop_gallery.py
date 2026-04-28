# TITLE: Face Crop Gallery
# TITLE_VI: Bộ Sưu Tập Khuôn Mặt
# LEVEL: Intermediate
# ICON: 🖼️
# COLOR: #eab308
# DESC: Detect faces, crop them, and save to a gallery.
# DESC_VI: Phát hiện khuôn mặt, cắt và lưu vào bộ sưu tập.
# ORDER: 43
# ============================================================



import ai_vision
import camera
import display

# Step 1: Load the AI face detection model
detector = ai_vision.Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Face Crop Gallery ready!")

# Step 3: Keep a counter for saved face images
save_count = 0

# Step 4: Detect faces, crop the first one, and save it
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Run AI face detection on the current frame
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    retval, faces = detector.detect(camera_frame)

    # Crop the first detected face from the frame
    cropped_face = ai_vision.Crop_Detection(camera_frame = camera_frame, results = faces, index = 0)

    # If a face was found, save the cropped image to disk
    if cropped_face is not None:
        save_count = save_count + 1
        camera.Save_Frame(camera_frame = cropped_face, file_path = f"face_{save_count}.jpg")

    # Show the full camera frame with detection results
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Faces Saved', var_value = save_count)

camera.Close_Camera(capture_camera = capture_camera)
