# 💡 Hint: Edge Detection

## Goal
Detect edges in images.

## Main Hint
Use the `detect_edges()` function to find edges.

**Note:**
- Result will be a black and white image with highlighted edges
- Works best with high contrast images

## Code Structure
```python
# 1. Initialize camera
# 2. In the loop:
#    - Get frame
#    - Detect edges: edges_frame = detect_edges(camera_frame=...)
#    - Display edge image
# 3. Close camera
```

## Required Function:
- `detect_edges(camera_frame=...)` - Detect edges

