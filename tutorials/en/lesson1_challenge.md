# Lesson 1 - Challenge: Smart Photo Booth
## Challenge
Create a photo booth with mirror effect and automatic photo capture.

## Requirements
1. Initialize the camera
2. Display video with mirror effect (horizontal flip)
3. After 3 seconds (about 90 frames), automatically capture and save photo
4. Save the photo with name "photo_booth_1.jpg"
5. Continue displaying video
6. Close camera when done

## Hints
- Use a counter variable `frame_count` to count frames
- Each iteration, increment `frame_count` by 1
- When `frame_count == 90`, call `Save_Frame()` to save the photo
- Reset `frame_count = 0` after capturing to enable continuous capture

## Required Functions
- `Init_Camera()`, `Get_Camera_Frame()`, `Close_Camera()`
- `flip_image(input_image, direction="horizontal")`
- `Save_Frame(camera_frame, file_path)`
- `Show_Image(camera_frame)`

## Learning Objectives
Combine multiple skills: flip image, count frames, automatic photo saving.

