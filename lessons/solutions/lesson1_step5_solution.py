# SOLUTION: Lesson 1 - Step 5: Rotate Image
# This is the correct solution for step 5

import camera
import image
import display

capture_camera = camera.Init_Camera()
print("[OK] Rotation ready!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    rotated_frame = image.rotate_image(input_image = camera_frame, angle = 90)
    display.Show_Image(camera_frame = rotated_frame)

camera.Close_Camera(capture_camera = capture_camera)
