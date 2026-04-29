# Lesson 2 - Step 5: Filter Chain
## Task
Combine multiple filters together.

## Instructions
1. Initialize the camera
2. In the loop, get a frame
3. Convert image to grayscale
4. Blur the grayscale image
5. Detect edges on the blurred image
6. Display the final result
7. Close the camera

## Required Functions
- `Init_Camera()` - Initialize camera
- `Get_Camera_Frame(capture_camera)` - Get frame
- `convert_to_gray(input_image)` - Convert to grayscale
- `apply_blur(input_image, kernel_size)` - Blur
- `detect_edges(input_image, threshold1, threshold2)` - Detect edges
- `Show_Image(camera_frame)` - Display image
- `Close_Camera(capture_camera)` - Close camera

## Hints
- The output of one filter becomes the input of the next
- The order of filters is very important
- Blurring before edge detection helps reduce noise

