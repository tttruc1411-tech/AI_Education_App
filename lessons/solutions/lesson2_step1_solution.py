# SOLUTION: Lesson 2 - Step 1: Image Filters Lab
# This is the correct solution for step 1

import camera
import image
import display

capture_camera = camera.Init_Camera()
print("[OK] Filters Lab ready!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    gray_frame = image.convert_to_gray(input_image = camera_frame)
    display.Show_Image(camera_frame = gray_frame)

camera.Close_Camera(capture_camera = capture_camera)
