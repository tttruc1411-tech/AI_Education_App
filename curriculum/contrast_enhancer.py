# TITLE: Contrast Enhancer
# TITLE_VI: Tăng Cường Độ Tương Phản
# LEVEL: Intermediate
# ICON: 🔆
# COLOR: #eab308
# DESC: Enhance image contrast and detect faces.
# DESC_VI: Tăng cường độ tương phản và phát hiện khuôn mặt.
# ORDER: 46
# ============================================================



import ai_vision
import camera
import display
import image

# Step 1: Load the AI face detection model
detector = ai_vision.Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Contrast Enhancer ready!")

# Step 3: Enhance contrast and run face detection on the enhanced image
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Enhance the contrast of the frame using histogram equalization
    enhanced = image.equalize_histogram(input_image = camera_frame)

    # Run AI face detection on the contrast-enhanced image
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = enhanced)
    retval, faces = detector.detect(enhanced)

    # Count how many faces were found in the enhanced image
    face_count = ai_vision.Get_Detection_Count(results = faces)

    # Show the enhanced image with detection results
    display.Show_Image(camera_frame = enhanced)
    display.Observe_Variable(var_name = 'Faces Detected', var_value = face_count)

camera.Close_Camera(capture_camera = capture_camera)
