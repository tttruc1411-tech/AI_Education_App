# Lesson 1 - Step 3: Mirror Selfie Mode
## Task
Flip the camera image horizontally like a mirror.

## Instructions
1. Initialize the camera
2. In the loop, get a frame from the camera
3. Use `flip_image()` with `direction="horizontal"` to flip the image
4. Display the flipped image
5. Close the camera when done

## Required Functions
- `Init_Camera()` - Initialize the camera
- `Get_Camera_Frame(capture_camera)` - Get a frame
- `flip_image(input_image, direction)` - Flip the image
- `Show_Image(camera_frame)` - Display the image
- `Close_Camera(capture_camera)` - Close the camera

## Hints
- `direction="horizontal"` to flip horizontally (like a mirror)
- `direction="vertical"` to flip vertically
- `direction="both"` to flip both ways

