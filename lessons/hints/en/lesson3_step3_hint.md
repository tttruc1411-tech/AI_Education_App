# 💡 Hint: Multiple Shapes

## Goal
Draw multiple different shapes on the same image.

## Main Hint
Call multiple drawing functions sequentially on the same frame.

**Example:**
```python
# Draw rectangle
Draw_Rectangle(camera_frame=frame, x=50, y=50, width=100, height=80, color=green)

# Draw circle
Draw_Circle(camera_frame=frame, center_x=200, center_y=200, radius=40, color=red)

# Draw another rectangle
Draw_Rectangle(camera_frame=frame, x=300, y=100, width=120, height=90, color=blue)
```

## Code Structure
```python
# 1. Initialize camera
# 2. In the loop:
#    - Get frame
#    - Draw shape 1
#    - Draw shape 2
#    - Draw shape 3
#    - Display image
# 3. Close camera
```

## Note:
- All shapes are drawn on the same `camera_frame`
- Later shapes will overlay earlier shapes if positions overlap

