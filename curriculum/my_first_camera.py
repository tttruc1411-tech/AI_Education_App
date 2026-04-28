# TITLE: My First Camera
# TITLE_VI: Camera Đầu Tiên Của Em
# LEVEL: Beginner
# ICON: 📷
# COLOR: #22c55e
# DESC: Learn the basics of camera programming.
# DESC_VI: Học những kiến thức cơ bản về lập trình camera.
# ORDER: 4
# ============================================================



import camera
import display

# Step 1: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Camera is ready!")

# Step 2: Show live video in a loop
while True:
    # Grab one frame (picture) from the camera
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Send the frame to the Live Feed panel
    display.Show_Image(camera_frame = camera_frame)

# Step 3: Clean up when done
camera.Close_Camera(capture_camera = capture_camera)
print("[OK] Camera closed.")
