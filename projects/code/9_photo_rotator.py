# TITLE: Photo Rotator
# TITLE_VI: Xoay Hình Ảnh
# LEVEL: Beginner
# ICON: 🔄
# COLOR: #22c55e
# DESC: Rotate your camera feed.
# DESC_VI: Xoay hình ảnh từ camera của bạn.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import rotation function
from src.modules.library.functions.image_processing import rotate_image
# Import variable block to set the angle
from src.modules.library.functions.variables import Create_Number
# Import display blocks
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable

# Step 1: Create an angle variable (try changing this value!)
angle = Create_Number(value = 45)

# Step 2: Start the camera
capture_camera = Init_Camera()
print("[OK] Photo Rotator ready!")

# Step 3: Rotate every frame by the angle
while True:
    # Grab a frame from the camera
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Rotate the image around its center
    rotated = rotate_image(input_image = camera_frame, angle = angle)

    # Show the rotated image
    Show_Image(camera_frame = rotated)

    # Display the current angle in the Results panel
    Observe_Variable(var_name = 'Angle', var_value = angle)

# Clean up
Close_Camera(capture_camera = capture_camera)
