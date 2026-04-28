# TITLE: Threshold Lab
# TITLE_VI: Phòng Thí Nghiệm Ngưỡng
# LEVEL: Beginner
# ICON: 🔬
# COLOR: #22c55e
# DESC: Turn images into black and white using a threshold cutoff.
# DESC_VI: Chuyển hình ảnh thành đen trắng bằng ngưỡng cắt.
# ORDER: 39
# ============================================================



import camera
import display
import image
import variables

# Step 1: Create a threshold cutoff variable (0–255)
# Pixels brighter than this value become white; darker ones become black.
# Try changing this number to see how it affects the result!
cutoff = variables.Create_Number(value = 127)

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Threshold Lab ready!")

# Step 3: Apply thresholding on every frame
while True:
    # Grab a frame from the camera
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Convert the frame to black & white using our cutoff value
    # Pixels above the cutoff become white (255), below become black (0)
    thresh_image = image.threshold_image(input_image = camera_frame, threshold = cutoff)

    # Show the thresholded image in the Live Feed
    display.Show_Image(camera_frame = thresh_image)

    # Display the current cutoff value in the Results panel
    display.Observe_Variable(var_name = 'Cutoff', var_value = cutoff)

# Clean up
camera.Close_Camera(capture_camera = capture_camera)
