# TITLE: Image Filters Lab
# TITLE_VI: Phòng Thí Nghiệm Bộ Lọc Ảnh
# LEVEL: Beginner
# ICON: 🎨
# COLOR: #22c55e
# DESC: Apply cool filters to your camera feed.
# DESC_VI: Áp dụng các bộ lọc thú vị lên hình ảnh camera.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import image processing filters
from src.modules.library.functions.image_processing import convert_to_gray, apply_blur, detect_edges, flip_image
# Import display block
from src.modules.library.functions.display_blocks import Show_Image

# Step 1: Start the camera
capture_camera = Init_Camera()
print("[OK] Filters Lab ready!")

# Step 2: Apply a chain of filters in a loop
while True:
    # Grab a frame from the camera
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Filter 1: Convert color image to grayscale
    gray = convert_to_gray(input_image = camera_frame)

    # Filter 2: Blur the image to smooth it out
    blurred = apply_blur(input_image = gray, kernel_size = 5)

    # Filter 3: Find edges in the blurred image
    edges = detect_edges(input_image = blurred, threshold1 = 100, threshold2 = 200)

    # Filter 4: Flip the result horizontally for fun
    flipped = flip_image(input_image = edges, direction = 'horizontal')

    # Show the final filtered image
    Show_Image(camera_frame = blurred)

# Clean up
Close_Camera(capture_camera = capture_camera)
