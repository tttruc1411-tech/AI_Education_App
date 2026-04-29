# SOLUTION: Lesson 2 - Challenge: Artistic Filter Pipeline
# This is the correct solution for the challenge

import camera
import image
import display

capture_camera = camera.Init_Camera()

print("[OK] Artistic filter ready!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    
    gray_frame = image.convert_to_gray(input_image = camera_frame)
    
    blurred_frame = image.apply_blur(input_image = gray_frame, kernel_size = 15)
    
    edges_frame = image.detect_edges(input_image = blurred_frame, threshold1 = 100, threshold2 = 200)
    
    final_frame = image.flip_image(input_image = edges_frame, direction = 'horizontal')
    
    display.Show_Image(camera_frame = final_frame)

camera.Close_Camera(capture_camera = capture_camera)
