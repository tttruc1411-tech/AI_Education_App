# SOLUTION: Lesson 2 - Step 4: Resize Image
# This is the correct solution for step 4

import camera
import image
import display

capture_camera = camera.Init_Camera()
print("[OK] Resize ready!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    resized_frame = image.resize_image(input_image = camera_frame, width = 320, height = 240)
    display.Show_Image(camera_frame = resized_frame)

camera.Close_Camera(capture_camera = capture_camera)
