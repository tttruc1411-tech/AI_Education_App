# TITLE: Brightness Controller
# TITLE_VI: Điều Khiển Độ Sáng
# LEVEL: Beginner
# ICON: ☀️
# COLOR: #22c55e
# DESC: Control image brightness with variables.
# DESC_VI: Điều khiển độ sáng hình ảnh bằng biến số.
# ============================================================



import camera
import display
import image
import variables

# Step 1: Create a brightness factor variable (>1 = brighter, <1 = darker)
factor = variables.Create_Decimal(value = 1.5)

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Brightness controller ready!")

# Step 3: Adjust brightness on every frame
while True:
    # Grab a frame from the camera
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Make the image brighter or darker using our factor
    bright_frame = image.adjust_brightness(input_image = camera_frame, factor = factor)

    # Show the adjusted image in the Live Feed
    display.Show_Image(camera_frame = bright_frame)

    # Display the current brightness factor in the Results panel
    display.Observe_Variable(var_name = 'Brightness', var_value = factor)

# Clean up
camera.Close_Camera(capture_camera = capture_camera)
