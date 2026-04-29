# SOLUTION: Lesson 3 - Step 1: Draw Rectangle
# This is the correct solution for step 1

import camera
import display

capture_camera = camera.Init_Camera()
print("[OK] Drawing ready!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    camera_frame = display.Draw_Rectangle(camera_frame = camera_frame, x = 100, y = 100, width = 200, height = 150, color = "green")
    display.Show_Image(camera_frame = camera_frame)

camera.Close_Camera(capture_camera = capture_camera)
