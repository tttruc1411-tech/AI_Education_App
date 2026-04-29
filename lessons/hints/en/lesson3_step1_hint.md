# 💡 Hint: Draw Rectangle

## Goal
Draw a rectangle on images.

## Main Hint
Use the `Draw_Rectangle()` function with position and size parameters.

**Parameters:**
- `x, y` = Coordinates of top-left corner
- `width, height` = Width and height
- `color` = Color (green, red, blue, yellow, white)

**Example:**
```python
Draw_Rectangle(camera_frame=frame, x=100, y=100, width=200, height=150, color=green)
```

## Code Structure
```python
# 1. Initialize camera
# 2. In the loop:
#    - Get frame
#    - Draw rectangle
#    - Display image
# 3. Close camera
```

## Required Function:
- `Draw_Rectangle(camera_frame=..., x=..., y=..., width=..., height=..., color=...)` - Draw rectangle

