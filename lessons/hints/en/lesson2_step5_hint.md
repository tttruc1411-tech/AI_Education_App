# 💡 Hint: Filter Chain

## Goal
Combine multiple filters together.

## Main Hint
Apply multiple effects sequentially to the same image.

**Example filter chain:**
1. Convert to grayscale
2. Apply blur
3. Detect edges

## Code Structure
```python
# 1. Initialize camera
# 2. In the loop:
#    - Get frame
#    - Filter 1: gray = convert_to_gray(camera_frame=...)
#    - Filter 2: blurred = apply_blur(camera_frame=gray, blur_amount=15)
#    - Filter 3: edges = detect_edges(camera_frame=blurred)
#    - Display final result
# 3. Close camera
```

## Note:
- Output of previous filter is input of next filter
- Order of filters affects the final result

## Required Functions:
- `convert_to_gray()` - Grayscale
- `apply_blur()` - Blur
- `detect_edges()` - Edges

