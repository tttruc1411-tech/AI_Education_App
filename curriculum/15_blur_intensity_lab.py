# TITLE: Blur Intensity Lab
# TITLE_VI: Phòng Thí Nghiệm Độ Mờ
# LEVEL: Beginner
# ICON: 💨
# COLOR: #22c55e
# DESC: Experiment with blur effects.
# DESC_VI: Thí nghiệm với hiệu ứng làm mờ.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import blur function
from src.modules.library.functions.image_processing import apply_blur
# Import variable block to control blur strength
from src.modules.library.functions.variables import Create_Number
# Import display blocks
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable

# Step 1: Create a kernel size variable (must be an odd number: 3, 5, 7, 9...)
# Bigger number = more blur!
kernel_size = Create_Number(value = 7)

# Step 2: Start the camera
capture_camera = Init_Camera()
print("[OK] Blur Intensity Lab ready!")

# Step 3: Apply blur on every frame
while True:
    # Grab a frame from the camera
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Apply Gaussian blur with our kernel size
    blurred = apply_blur(input_image = camera_frame, kernel_size = kernel_size)

    # Show the blurred image
    Show_Image(camera_frame = blurred)

    # Display the kernel size in the Results panel
    Observe_Variable(var_name = 'Kernel Size', var_value = kernel_size)

# Clean up
Close_Camera(capture_camera = capture_camera)
