# Lesson 3 - Step 2: Draw Circle
## Task
Draw a circle on camera images.

## Instructions
1. Initialize the camera
2. In the loop, get a frame
3. Use `Draw_Circle()` with `center_x=320`, `center_y=240`, `radius=100`, `color="red"`
4. Display the image with circle
5. Close the camera

## Required Functions
- `Init_Camera()` - Initialize camera
- `Get_Camera_Frame(capture_camera)` - Get frame
- `Draw_Circle(camera_frame, center_x, center_y, radius, color)` - Draw circle
- `Show_Image(camera_frame)` - Display image
- `Close_Camera(capture_camera)` - Close camera

## Hints
- `center_x, center_y` are the coordinates of the circle center
- `radius` is the radius
- Available colors: "green", "red", "blue", "yellow", "white"

