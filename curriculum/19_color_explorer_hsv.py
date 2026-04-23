# TITLE: Color Explorer with HSV
# TITLE_VI: Khám Phá Màu Sắc HSV
# LEVEL: Intermediate
# ICON: 🎨
# COLOR: #eab308
# DESC: Analyze colors with HSV color space.
# DESC_VI: Phân tích màu sắc với không gian màu HSV.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import image processing blocks
from src.modules.library.functions.image_processing import convert_to_hsv, adjust_brightness, draw_text
# Import display blocks
from src.modules.library.functions.display_blocks import Show_Image, Draw_Rectangle

# Step 1: Start the camera
capture_camera = Init_Camera()
print("[OK] Color Explorer ready!")

# Step 2: Explore HSV colors on each frame
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Convert the frame to HSV color space (Hue, Saturation, Value)
    hsv_frame = convert_to_hsv(input_image = camera_frame)

    # Brighten the HSV image to make colors more vivid
    bright_hsv = adjust_brightness(input_image = hsv_frame, factor = 1.3)

    # Draw a rectangle to highlight the center region of interest
    bright_hsv = Draw_Rectangle(camera_frame = bright_hsv, x = 200, y = 150, width = 240, height = 180, color = 'green')

    # Add a label showing the color space
    bright_hsv = draw_text(input_image = bright_hsv, text = 'HSV Color Space', x = 10, y = 30)

    # Stream the annotated HSV image
    Show_Image(camera_frame = bright_hsv)

Close_Camera(capture_camera = capture_camera)
