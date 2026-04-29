# Lesson 1 - Step 4: Brightness Control
## Task
Adjust the brightness of the camera image.

## Instructions
1. Initialize the camera
2. In the loop, get a frame
3. Use `adjust_brightness()` with `factor=1.5` to increase brightness
4. Display the adjusted image
5. Close the camera

## Required Functions
- `Init_Camera()` - Initialize the camera
- `Get_Camera_Frame(capture_camera)` - Get a frame
- `adjust_brightness(input_image, factor)` - Adjust brightness
- `Show_Image(camera_frame)` - Display the image
- `Close_Camera(capture_camera)` - Close the camera

## Hints
- `factor > 1.0` to increase brightness (e.g., 1.5 = 50% brighter)
- `factor < 1.0` to decrease brightness (e.g., 0.5 = 50% darker)
- `factor = 1.0` to keep unchanged

