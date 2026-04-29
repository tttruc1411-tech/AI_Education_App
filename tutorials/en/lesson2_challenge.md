# Lesson 2 - Challenge: Artistic Filter Pipeline
## Challenge
Create a unique artistic filter.

## Requirements
Create an artistic effect by combining at least 3 filters:
1. Initialize the camera
2. Apply filter chain in order:
   - Convert to grayscale
   - Blur with `kernel_size=7`
   - Detect edges with `threshold1=50`, `threshold2=150`
   - Flip image horizontally
3. Display the result
4. Close camera when done

## Required Functions
- `Init_Camera()`, `Get_Camera_Frame()`, `Close_Camera()`
- `convert_to_gray(input_image)`
- `apply_blur(input_image, kernel_size)`
- `detect_edges(input_image, threshold1, threshold2)`
- `flip_image(input_image, direction)`
- `Show_Image(camera_frame)`

## Learning Objectives
Combine all learned image processing skills to create artistic effects.

## Hints
- Try changing parameters to create different effects
- You can add or remove filters to be creative

