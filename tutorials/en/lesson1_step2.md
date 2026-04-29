# Lesson 1 - Step 2: Save & Load Pictures
## Task
Capture a photo from the camera and save it to disk, then load it back.

## Instructions
1. Initialize the camera
2. Get a frame from the camera
3. Use `Save_Frame()` to save the image with name "my_photo.jpg"
4. Use `Load_Image()` to load the saved image
5. Display the loaded image
6. Close the camera

## Required Functions
- `Init_Camera()` - Initialize the camera
- `Get_Camera_Frame(capture_camera)` - Get a frame
- `Save_Frame(camera_frame, file_path)` - Save the image
- `Load_Image(file_path)` - Load image from disk
- `Show_Image(camera_frame)` - Display the image
- `Close_Camera(capture_camera)` - Close the camera

## Hints
- Images will be saved to the `projects/data/saved/` folder
- The filename can be "my_photo.jpg" or any name you want

