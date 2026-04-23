# TITLE: FPS Performance Monitor
# TITLE_VI: Theo Dõi Hiệu Suất FPS
# LEVEL: Intermediate
# ICON: ⚡
# COLOR: #eab308
# DESC: Measure how fast your code runs.
# DESC_VI: Đo tốc độ chạy của chương trình.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import image processing blocks to add computational cost
from src.modules.library.functions.image_processing import convert_to_gray, detect_edges
# Import display blocks
from src.modules.library.functions.display_blocks import Show_Image, Show_FPS

# Step 1: Start the camera
capture_camera = Init_Camera()
print("[OK] FPS Performance Monitor ready!")

# Step 2: Process frames and measure speed
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Apply grayscale conversion (adds processing time)
    gray = convert_to_gray(input_image = camera_frame)

    # Apply edge detection (adds more processing time)
    edges = detect_edges(input_image = gray, threshold1 = 100, threshold2 = 200)

    # Overlay the FPS counter to see how fast we're running
    edges = Show_FPS(camera_frame = edges)

    # Stream the result with FPS overlay
    Show_Image(camera_frame = edges)

Close_Camera(capture_camera = capture_camera)
