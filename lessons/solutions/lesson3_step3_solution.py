# SOLUTION: Lesson 3 - Step 3: Multiple Shapes
# This is the correct solution for step 3

import camera
import display

capture_camera = camera.Init_Camera()
print("[OK] Multiple shapes ready!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    camera_frame = display.Draw_Rectangle(camera_frame = camera_frame, x = 50, y = 50, width = 150, height = 100, color = "green")
    camera_frame = display.Draw_Circle(camera_frame = camera_frame, center_x = 320, center_y = 240, radius = 80, color = "red")
    camera_frame = display.Draw_Rectangle(camera_frame = camera_frame, x = 450, y = 350, width = 150, height = 100, color = "yellow")
    display.Show_Image(camera_frame = camera_frame)

camera.Close_Camera(capture_camera = capture_camera)
