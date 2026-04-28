# TITLE: Hi-Res Capture Station
# TITLE_VI: Trạm Chụp Ảnh Cao Cấp
# LEVEL: Advanced
# ICON: 📸
# COLOR: #f97316
# DESC: Switch to high resolution and capture a snapshot when a face is detected.
# DESC_VI: Chuyển sang độ phân giải cao và chụp ảnh khi phát hiện khuôn mặt.
# ORDER: 50
# ============================================================



import ai_vision
import camera
import display
import logic

# Step 1: Load the AI face detection model
detector = ai_vision.Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera at low resolution for fast detection
capture_camera = camera.Init_Camera()
camera.Set_Camera_Resolution(capture_camera = capture_camera, width = 640, height = 480)
print("[OK] Hi-Res Capture Station ready!")

# Step 3: Track how many snapshots have been saved
snapshot_count = 0

# Step 4: Detect faces at low res, then switch to high res to capture
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Run AI face detection on the low-res frame
    ai_vision.Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    retval, faces = detector.detect(camera_frame)

    # Count faces detected in this frame
    face_count = ai_vision.Get_Detection_Count(results = faces)

    # When a face is detected, switch to high res and capture a snapshot
    if face_count > 0:
        # Switch to high resolution for a crisp capture
        camera.Set_Camera_Resolution(capture_camera = capture_camera, width = 1280, height = 720)

        # Capture a high-res snapshot with a 3-second countdown
        snapshot = camera.Capture_Snapshot(capture_camera = capture_camera, countdown = 3)

        # Save the hi-res snapshot to disk
        snapshot_count = snapshot_count + 1
        camera.Save_Frame(camera_frame = snapshot, file_path = f"hi_res_{snapshot_count}.jpg")

        timestamp = logic.Get_Timestamp()
        logic.Print_Message(message = f"[{timestamp}] Hi-res snapshot #{snapshot_count} saved!")

        # Switch back to low resolution for fast detection
        camera.Set_Camera_Resolution(capture_camera = capture_camera, width = 640, height = 480)

    # Overlay capture status on the frame
    camera_frame = display.Draw_Text_Box(camera_frame = camera_frame, text = f"Snapshots: {snapshot_count}", x = 10, y = 10, bg_color = 'blue', text_color = 'white')

    # Stream the low-res detection feed and track stats
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'Faces', var_value = face_count)
    display.Observe_Variable(var_name = 'Snapshots', var_value = snapshot_count)

camera.Close_Camera(capture_camera = capture_camera)
