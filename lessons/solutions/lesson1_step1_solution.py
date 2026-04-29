# SOLUTION: Lesson 1 - Step 1: My First Camera
# This is the correct solution for step 1

import camera
import display

capture_camera = camera.Init_Camera()
print("[OK] Camera is ready!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    display.Show_Image(camera_frame = camera_frame)

camera.Close_Camera(capture_camera = capture_camera)
print("[OK] Camera closed.")
