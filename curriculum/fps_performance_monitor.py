# TITLE: FPS Performance Monitor
# TITLE_VI: Theo Dõi Hiệu Suất FPS
# LEVEL: Intermediate
# ICON: ⚡
# COLOR: #eab308
# DESC: Measure how fast your code runs.
# DESC_VI: Đo tốc độ chạy của chương trình.
# ORDER: 22
# ============================================================



import camera
import display
import image

# Step 1: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] FPS Performance Monitor ready!")

# Step 2: Process frames and measure speed
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Apply grayscale conversion (adds processing time)
    gray = image.convert_to_gray(input_image = camera_frame)

    # Apply edge detection (adds more processing time)
    edges = image.detect_edges(input_image = gray, threshold1 = 100, threshold2 = 200)

    # Overlay the FPS counter to see how fast we're running
    edges = display.Show_FPS(camera_frame = edges)

    # Stream the result with FPS overlay
    display.Show_Image(camera_frame = edges)

camera.Close_Camera(capture_camera = capture_camera)
