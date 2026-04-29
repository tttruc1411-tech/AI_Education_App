# SOLUTION: Lesson 2 - Step 2: Blur Effect
# This is the correct solution for step 2

import camera
import image
import display

capture_camera = camera.Init_Camera()
print("[OK] Blur effect ready!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    blurred_frame = image.apply_blur(input_image = camera_frame, kernel_size = 15)
    display.Show_Image(camera_frame = blurred_frame)

camera.Close_Camera(capture_camera = capture_camera)
