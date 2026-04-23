# TITLE: Mirror Selfie Mode
# TITLE_VI: Chế Độ Gương Selfie
# LEVEL: Beginner
# ICON: 🪞
# COLOR: #22c55e
# DESC: Create a real-time mirror effect.
# DESC_VI: Tạo hiệu ứng gương trong thời gian thực.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import flip function for the mirror effect
from src.modules.library.functions.image_processing import flip_image
# Import display block
from src.modules.library.functions.display_blocks import Show_Image

# Step 1: Start the camera
capture_camera = Init_Camera()
print("[OK] Mirror mode activated!")

# Step 2: Flip the camera feed horizontally like a mirror
while True:
    # Grab a frame from the camera
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Flip horizontally — just like looking in a mirror!
    mirror_frame = flip_image(input_image = camera_frame, direction = 'horizontal')

    # Show the mirror image
    Show_Image(camera_frame = mirror_frame)

# Clean up
Close_Camera(capture_camera = capture_camera)
