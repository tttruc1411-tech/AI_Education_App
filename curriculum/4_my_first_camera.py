# TITLE: My First Camera
# TITLE_VI: Camera Đầu Tiên Của Em
# LEVEL: Beginner
# ICON: 📷
# COLOR: #22c55e
# DESC: Learn the basics of camera programming.
# DESC_VI: Học những kiến thức cơ bản về lập trình camera.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import display block to show the live feed
from src.modules.library.functions.display_blocks import Show_Image

# Step 1: Start the camera
capture_camera = Init_Camera()
print("[OK] Camera is ready!")

# Step 2: Show live video in a loop
while True:
    # Grab one frame (picture) from the camera
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Send the frame to the Live Feed panel
    Show_Image(camera_frame = camera_frame)

# Step 3: Clean up when done
Close_Camera(capture_camera = capture_camera)
print("[OK] Camera closed.")
