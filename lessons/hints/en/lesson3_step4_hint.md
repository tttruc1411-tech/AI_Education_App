# 💡 Hint: Color Variations

## Goal
Draw multiple shapes with different colors.

## Main Hint
Use different colors for each shape.

**Available colors:**
- `green` = Green
- `red` = Red
- `blue` = Blue
- `yellow` = Yellow
- `white` = White

**Example:**
```python
# Green rectangle
Draw_Rectangle(camera_frame=frame, x=50, y=50, width=100, height=80, color=green)

# Red circle
Draw_Circle(camera_frame=frame, center_x=200, center_y=150, radius=40, color=red)

# Blue rectangle
Draw_Rectangle(camera_frame=frame, x=300, y=200, width=80, height=100, color=blue)

# Yellow circle
Draw_Circle(camera_frame=frame, center_x=400, center_y=300, radius=50, color=yellow)
```

## Code Structure
```python
# 1. Initialize camera
# 2. In the loop:
#    - Get frame
#    - Draw multiple shapes with different colors
#    - Display image
# 3. Close camera
```

## Experiment:
- Try drawing at least 4 shapes with 4 different colors
- Arrange positions to look nice

