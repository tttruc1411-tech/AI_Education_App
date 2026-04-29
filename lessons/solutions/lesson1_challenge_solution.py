# SOLUTION: Lesson 1 - Challenge: Smart Photo Booth
# This is the correct solution for the challenge

import camera
import image
import display

capture_camera = camera.Init_Camera()

frame_count = 0

print("[OK] Photo Booth ready! Smile in 3 seconds...")

while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    
    flipped_frame = image.flip_image(input_image = camera_frame, direction = 'horizontal')
    
    display.Show_Image(camera_frame = flipped_frame)
    
    frame_count += 1
    
    if frame_count == 90:
        camera.Save_Frame(camera_frame = flipped_frame, file_path = 'photo_booth.jpg')
        print("[OK] Photo captured!")
        frame_count = 0

camera.Close_Camera(capture_camera = capture_camera)
