# 💡 Hint: Blur Effect

## Goal
Apply blur effect to images.

## Main Hint
Use the `apply_blur()` function with parameter `blur_amount`.

**blur_amount values:**
- Must be an odd number: 3, 5, 7, 9, 11, ...
- Larger number = More blur
- Recommended: Start with `blur_amount=15`

## Code Structure
```python
# 1. Initialize camera
# 2. In the loop:
#    - Get frame
#    - Blur: blurred_frame = apply_blur(camera_frame=..., blur_amount=15)
#    - Display blurred image
# 3. Close camera
```

## Required Function:
- `apply_blur(camera_frame=..., blur_amount=...)` - Blur image

