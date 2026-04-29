# SOLUTION: Lesson 2 - Step 5: Filter Chain
# This is the correct solution for step 5

import camera
import image
import display

capture_camera = camera.Init_Camera()
print("[OK] Filter chain ready!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    gray_frame = image.convert_to_gray(input_image = camera_frame)
    blurred_frame = image.apply_blur(input_image = gray_frame, kernel_size = 5)
    edges_frame = image.detect_edges(input_image = blurred_frame, threshold1 = 100, threshold2 = 200)
    display.Show_Image(camera_frame = edges_frame)

camera.Close_Camera(capture_camera = capture_camera)
