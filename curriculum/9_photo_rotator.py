# TITLE: Photo Rotator
# TITLE_VI: Xoay Hình Ảnh
# LEVEL: Beginner
# ICON: 🔄
# COLOR: #22c55e
# DESC: Rotate your camera feed.
# DESC_VI: Xoay hình ảnh từ camera của bạn.
# ============================================================



import camera
import display
import image
import variables

# Step 1: Create an angle variable (try changing this value!)
angle = variables.Create_Number(value = 45)

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Photo Rotator ready!")

# Step 3: Rotate every frame by the angle
while True:
    # Grab a frame from the camera
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Rotate the image around its center
    rotated = image.rotate_image(input_image = camera_frame, angle = angle)

    # Show the rotated image
    display.Show_Image(camera_frame = rotated)

    # Display the current angle in the Results panel
    display.Observe_Variable(var_name = 'Angle', var_value = angle)

# Clean up
camera.Close_Camera(capture_camera = capture_camera)
