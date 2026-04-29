# SOLUTION: Lesson 3 - Step 4: Color Variations
# This is the correct solution for step 4

import camera
import display

capture_camera = camera.Init_Camera()
print("[OK] Color variations ready!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    camera_frame = display.Draw_Circle(camera_frame = camera_frame, center_x = 100, center_y = 100, radius = 50, color = "green")
    camera_frame = display.Draw_Circle(camera_frame = camera_frame, center_x = 540, center_y = 100, radius = 50, color = "red")
    camera_frame = display.Draw_Circle(camera_frame = camera_frame, center_x = 100, center_y = 380, radius = 50, color = "blue")
    camera_frame = display.Draw_Circle(camera_frame = camera_frame, center_x = 540, center_y = 380, radius = 50, color = "yellow")
    display.Show_Image(camera_frame = camera_frame)

camera.Close_Camera(capture_camera = capture_camera)
