# TITLE: Grayscale Converter
# TITLE_VI: Chuyển Đổi Ảnh Xám
# LEVEL: Beginner
# ICON: ⬛
# COLOR: #22c55e
# DESC: Convert colors to grayscale.
# DESC_VI: Chuyển đổi ảnh màu sang ảnh xám.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import grayscale conversion function
from src.modules.library.functions.image_processing import convert_to_gray
# Import display block
from src.modules.library.functions.display_blocks import Show_Image

# Step 1: Start the camera
capture_camera = Init_Camera()
print("[OK] Grayscale Converter ready!")

# Step 2: Convert every frame to grayscale
while True:
    # Grab a color frame from the camera (BGR = Blue, Green, Red channels)
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Convert to grayscale — this combines all 3 color channels into 1
    # The formula is roughly: Gray = 0.299*Red + 0.587*Green + 0.114*Blue
    # Human eyes are most sensitive to green, so green has the highest weight!
    gray_image = convert_to_gray(input_image = camera_frame)

    # Show the grayscale result
    Show_Image(camera_frame = gray_image)

# Clean up
Close_Camera(capture_camera = capture_camera)
