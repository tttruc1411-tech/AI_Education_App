# TITLE: Night Vision Effect
# TITLE_VI: Hiệu Ứng Nhìn Đêm
# LEVEL: Advanced
# ICON: 🌙
# COLOR: #f97316
# DESC: Simulate a night-vision camera.
# DESC_VI: Mô phỏng camera nhìn đêm.
# ============================================================



import camera
import display
import image

# Step 1: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Night Vision Effect active!")

# Step 2: Apply a night-vision image processing pipeline
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Night-vision pipeline: convert to grayscale first
    camera_frame = image.convert_to_gray(input_image = camera_frame)

    # Boost brightness to simulate light amplification (factor > 1 = brighter)
    camera_frame = image.adjust_brightness(input_image = camera_frame, factor = 2.0)

    # Detect edges to add the classic night-vision wireframe look
    camera_frame = image.detect_edges(input_image = camera_frame, threshold1 = 50, threshold2 = 150)

    # Overlay the "NIGHT VISION" label for the authentic HUD feel
    camera_frame = image.draw_text(input_image = camera_frame, text = 'NIGHT VISION', x = 10, y = 60)

    # Show FPS to monitor processing performance
    camera_frame = display.Show_FPS(camera_frame = camera_frame)

    # Stream the night-vision feed
    display.Show_Image(camera_frame = camera_frame)

camera.Close_Camera(capture_camera = capture_camera)
