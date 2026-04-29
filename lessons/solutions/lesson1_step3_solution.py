# SOLUTION: Lesson 1 - Step 3: Mirror Selfie Mode
# This is the correct solution for step 3

import camera
import image
import display

capture_camera = camera.Init_Camera()
print("[OK] Mirror mode activated!")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    mirror_frame = image.flip_image(input_image = camera_frame, direction = 'horizontal')
    display.Show_Image(camera_frame = mirror_frame)

camera.Close_Camera(capture_camera = capture_camera)
