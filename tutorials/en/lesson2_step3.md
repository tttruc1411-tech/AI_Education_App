# Lesson 2 - Step 3: Edge Detection
## Task
Detect edges in images.

## Instructions
1. Initialize the camera
2. In the loop, get a frame
3. Use `detect_edges()` with `threshold1=100`, `threshold2=200`
4. Display the edge image
5. Close the camera

## Required Functions
- `Init_Camera()` - Initialize camera
- `Get_Camera_Frame(capture_camera)` - Get frame
- `detect_edges(input_image, threshold1, threshold2)` - Detect edges
- `Show_Image(camera_frame)` - Display image
- `Close_Camera(capture_camera)` - Close camera

## Hints
- `threshold1` and `threshold2` control edge detection sensitivity
- Lower values = detect more edges
- Higher values = only detect sharp edges

