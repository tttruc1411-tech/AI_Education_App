# Lesson 2 - Step 2: Blur Effect
## Task
Apply blur effect to images.

## Instructions
1. Initialize the camera
2. In the loop, get a frame
3. Use `apply_blur()` with `kernel_size=15` to blur the image
4. Display the blurred image
5. Close the camera

## Required Functions
- `Init_Camera()` - Initialize camera
- `Get_Camera_Frame(capture_camera)` - Get frame
- `apply_blur(input_image, kernel_size)` - Blur image
- `Show_Image(camera_frame)` - Display image
- `Close_Camera(capture_camera)` - Close camera

## Hints
- Larger `kernel_size` = more blur
- `kernel_size` must be an odd number (5, 7, 9, 11, 15, ...)
- Blurring helps reduce noise in images

