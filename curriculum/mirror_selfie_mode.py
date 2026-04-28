# TITLE: Mirror Selfie Mode
# TITLE_VI: Chế Độ Gương Selfie
# LEVEL: Beginner
# ICON: 🪞
# COLOR: #22c55e
# DESC: Create a real-time mirror effect.
# DESC_VI: Tạo hiệu ứng gương trong thời gian thực.
# ORDER: 7
# ============================================================



import camera
import display
import image

# Step 1: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Mirror mode activated!")

# Step 2: Flip the camera feed horizontally like a mirror
while True:
    # Grab a frame from the camera
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Flip horizontally — just like looking in a mirror!
    mirror_frame = image.flip_image(input_image = camera_frame, direction = 'horizontal')

    # Show the mirror image
    display.Show_Image(camera_frame = mirror_frame)

# Clean up
camera.Close_Camera(capture_camera = capture_camera)
