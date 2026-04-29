# 💡 Hint: Draw Circle

## Goal
Draw a circle on images.

## Main Hint
Use the `Draw_Circle()` function with center and radius.

**Parameters:**
- `center_x, center_y` = Coordinates of circle center
- `radius` = Radius
- `color` = Color (green, red, blue, yellow, white)

**Example:**
```python
Draw_Circle(camera_frame=frame, center_x=320, center_y=240, radius=50, color=red)
```

## Code Structure
```python
# 1. Initialize camera
# 2. In the loop:
#    - Get frame
#    - Draw circle
#    - Display image
# 3. Close camera
```

## Required Function:
- `Draw_Circle(camera_frame=..., center_x=..., center_y=..., radius=..., color=...)` - Draw circle

