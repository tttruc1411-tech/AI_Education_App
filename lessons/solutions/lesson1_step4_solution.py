# SOLUTION: Lesson 1 - Step 4: Brightness Control
# This is the correct solution for step 4

import camera
import image
import display

capture_camera = camera.Init_Camera()
print("[OK] Brightness controller ready!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    bright_frame = image.adjust_brightness(input_image = camera_frame, factor = 1.5)
    display.Show_Image(camera_frame = bright_frame)

camera.Close_Camera(capture_camera = capture_camera)
