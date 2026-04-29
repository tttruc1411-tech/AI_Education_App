# SOLUTION: Lesson 1 - Step 2: Save & Load Pictures
# This is the correct solution for step 2

import camera
import display

capture_camera = camera.Init_Camera()
print("[OK] Camera ready!")

camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

camera.Save_Frame(camera_frame = camera_frame, file_path = 'my_photo.jpg')

camera.Close_Camera(capture_camera = capture_camera)

loaded_image = camera.Load_Image(file_path = 'my_photo.jpg')

display.Show_Image(camera_frame = loaded_image)
print("[OK] Photo saved and loaded!")
