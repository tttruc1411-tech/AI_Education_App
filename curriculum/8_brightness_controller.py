# TITLE: Brightness Controller
# TITLE_VI: Điều Khiển Độ Sáng
# LEVEL: Beginner
# ICON: ☀️
# COLOR: #22c55e
# DESC: Control image brightness with variables.
# DESC_VI: Điều khiển độ sáng hình ảnh bằng biến số.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import brightness adjustment
from src.modules.library.functions.image_processing import adjust_brightness
# Import variable block to create a decimal number
from src.modules.library.functions.variables import Create_Decimal
# Import display blocks
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable

# Step 1: Create a brightness factor variable (>1 = brighter, <1 = darker)
factor = Create_Decimal(value = 1.5)

# Step 2: Start the camera
capture_camera = Init_Camera()
print("[OK] Brightness controller ready!")

# Step 3: Adjust brightness on every frame
while True:
    # Grab a frame from the camera
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Make the image brighter or darker using our factor
    bright_frame = adjust_brightness(input_image = camera_frame, factor = factor)

    # Show the adjusted image in the Live Feed
    Show_Image(camera_frame = bright_frame)

    # Display the current brightness factor in the Results panel
    Observe_Variable(var_name = 'Brightness', var_value = factor)

# Clean up
Close_Camera(capture_camera = capture_camera)
