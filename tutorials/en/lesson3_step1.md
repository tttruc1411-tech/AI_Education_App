# Lesson 3 - Step 1: Draw Rectangle
## Task
Draw a rectangle on camera images.

## Instructions
1. Initialize the camera
2. In the loop, get a frame
3. Use `Draw_Rectangle()` with `x=100`, `y=100`, `width=200`, `height=150`, `color="green"`
4. Display the image with rectangle
5. Close the camera

## Required Functions
- `Init_Camera()` - Initialize camera
- `Get_Camera_Frame(capture_camera)` - Get frame
- `Draw_Rectangle(camera_frame, x, y, width, height, color)` - Draw rectangle
- `Show_Image(camera_frame)` - Display image
- `Close_Camera(capture_camera)` - Close camera

## Hints
- `x, y` are the coordinates of the top-left corner
- `width, height` are the width and height
- Available colors: "green", "red", "blue", "yellow", "white"

