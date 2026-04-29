# SOLUTION: Lesson 3 - Challenge: Creative Art Canvas
# This is the correct solution for the challenge

import camera
import display

capture_camera = camera.Init_Camera()

print("[OK] Creative canvas ready!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    
    camera_frame = display.Draw_Rectangle(camera_frame = camera_frame, x = 200, y = 250, width = 200, height = 150, color = "blue")
    
    camera_frame = display.Draw_Rectangle(camera_frame = camera_frame, x = 200, y = 150, width = 200, height = 100, color = "red")
    
    camera_frame = display.Draw_Rectangle(camera_frame = camera_frame, x = 220, y = 280, width = 50, height = 50, color = "white")
    
    camera_frame = display.Draw_Rectangle(camera_frame = camera_frame, x = 330, y = 280, width = 50, height = 50, color = "white")
    
    camera_frame = display.Draw_Rectangle(camera_frame = camera_frame, x = 275, y = 320, width = 50, height = 80, color = "green")
    
    camera_frame = display.Draw_Circle(camera_frame = camera_frame, center_x = 500, center_y = 100, radius = 40, color = "yellow")
    
    display.Show_Image(camera_frame = camera_frame)

camera.Close_Camera(capture_camera = capture_camera)
