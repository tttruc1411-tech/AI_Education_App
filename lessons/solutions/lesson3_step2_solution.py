# SOLUTION: Lesson 3 - Step 2: Draw Circle
# This is the correct solution for step 2

import camera
import display

capture_camera = camera.Init_Camera()
print("[OK] Circle drawing ready!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    camera_frame = display.Draw_Circle(camera_frame = camera_frame, center_x = 320, center_y = 240, radius = 100, color = "red")
    display.Show_Image(camera_frame = camera_frame)

camera.Close_Camera(capture_camera = capture_camera)
