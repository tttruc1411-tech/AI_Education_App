# ============================================================
# LESSON 1: Camera Basics - Step 1
# TITLE: My First Camera
# TITLE_VI: Camera Đầu Tiên Của Em
# ============================================================

# Import camera and display modules
import camera
import display

# Step 1: Start the camera
# TODO: Initialize the camera and save it to the capture_camera variable
capture_camera = camera.Init_Camera()


print("[OK] Camera is ready!")

# Step 2: Show live video in a loop
while True:
    # TODO: Get a frame from the camera
    
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    # TODO: Display the frame on the Live Feed panel
    display.Show_Image(camera_frame = camera_frame)

# Step 3: Clean up when done
# TODO: Close the camera

print("[OK] Camera closed.")
camera.Close_Camera(capture_camera = capture_camera)
