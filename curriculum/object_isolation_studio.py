# TITLE: Object Isolation Studio
# TITLE_VI: Studio Tách Đối Tượng
# LEVEL: Advanced
# ICON: 🎯
# COLOR: #f97316
# DESC: Detect faces, crop and filter them, then display side by side.
# DESC_VI: Phát hiện khuôn mặt, cắt và lọc, rồi hiển thị cạnh nhau.
# ORDER: 49
# ============================================================



import ai_vision
import camera
import display
import image

# Step 1: Load the AI face detection model
detector = ai_vision.Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Object Isolation Studio ready!")

# Step 3: Detect faces, crop, apply a filter, and show side by side
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Run AI face detection on the current frame
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    retval, faces = detector.detect(camera_frame)

    # Crop the first detected face from the frame
    cropped_face = ai_vision.Crop_Detection(camera_frame = camera_frame, results = faces, index = 0)

    # If a face was found, apply a filter and stack with the original
    if cropped_face is not None:
        # Apply edge detection filter to the cropped face
        gray_face = image.convert_to_gray(input_image = cropped_face)
        filtered_face = image.detect_edges(input_image = gray_face, threshold1 = 100, threshold2 = 200)

        # Stack the original crop and filtered crop side by side
        comparison = display.Stack_Images(image1 = cropped_face, image2 = filtered_face, direction = 'horizontal')

        # Show the side-by-side comparison of original vs filtered crop
        display.Show_Image(camera_frame = comparison)
        display.Observe_Variable(var_name = 'Status', var_value = 'Face isolated')
    else:
        # No face detected — show the full camera feed
        display.Show_Image(camera_frame = camera_frame)
        display.Observe_Variable(var_name = 'Status', var_value = 'No face detected')

camera.Close_Camera(capture_camera = capture_camera)
