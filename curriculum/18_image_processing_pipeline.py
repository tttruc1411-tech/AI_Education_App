# TITLE: Image Processing Pipeline
# TITLE_VI: Chuỗi Xử Lý Hình Ảnh
# LEVEL: Intermediate
# ICON: 🔗
# COLOR: #eab308
# DESC: Chain multiple image effects together.
# DESC_VI: Kết hợp nhiều hiệu ứng hình ảnh với nhau.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import image processing blocks for the pipeline chain
from src.modules.library.functions.image_processing import convert_to_gray, apply_blur, detect_edges, adjust_brightness
# Import display blocks
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable

# Step 1: Start the camera
capture_camera = Init_Camera()
print("[OK] Image Processing Pipeline ready!")

# Step 2: Process each frame through a chain of effects
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Chain 1: Convert color image to grayscale
    gray = convert_to_gray(input_image = camera_frame)

    # Chain 2: Smooth the grayscale image with blur
    blurred = apply_blur(input_image = gray, kernel_size = 5)

    # Chain 3: Find edges in the blurred image
    edges = detect_edges(input_image = blurred, threshold1 = 50, threshold2 = 150)

    # Chain 4: Brighten the edge map so it's easier to see
    result = adjust_brightness(input_image = edges, factor = 1.5)

    # Stream the final processed image
    Show_Image(camera_frame = result)
    Observe_Variable(var_name = 'Pipeline Steps', var_value = 4)

Close_Camera(capture_camera = capture_camera)
