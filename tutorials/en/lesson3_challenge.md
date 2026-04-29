# Lesson 3 - Challenge: Creative Art Canvas
## Challenge
Create an artwork using shapes.

## Requirements
Create a simple "house" drawing by:
1. Initialize the camera
2. Draw a "house" consisting of:
   - House body: Blue rectangle (x=200, y=250, width=240, height=200)
   - Roof: Red rectangle (x=180, y=200, width=280, height=60)
   - Left window: Yellow rectangle (x=230, y=300, width=60, height=60)
   - Right window: Yellow rectangle (x=350, y=300, width=60, height=60)
   - Door: White rectangle (x=280, y=370, width=80, height=80)
3. Draw "sun": Yellow circle (center_x=550, center_y=100, radius=50)
4. Display the artwork
5. Close camera when done

## Required Functions
- `Init_Camera()`, `Get_Camera_Frame()`, `Close_Camera()`
- `Draw_Rectangle(camera_frame, x, y, width, height, color)`
- `Draw_Circle(camera_frame, center_x, center_y, radius, color)`
- `Show_Image(camera_frame)`

## Learning Objectives
Combine multiple shapes and colors to create a complete artwork.

## Hints
- Draw in order from bottom to top (body → roof → windows → door)
- You can add other details for decoration (grass, clouds, ...)

