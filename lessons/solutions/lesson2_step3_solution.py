# SOLUTION: Lesson 2 - Step 3: Edge Detection
# This is the correct solution for step 3

import camera
import image
import display

capture_camera = camera.Init_Camera()
print("[OK] Edge detection ready!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    edges_frame = image.detect_edges(input_image = camera_frame, threshold1 = 100, threshold2 = 200)
    display.Show_Image(camera_frame = edges_frame)

camera.Close_Camera(capture_camera = capture_camera)
