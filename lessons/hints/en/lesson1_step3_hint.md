# 💡 Hint: Mirror Selfie Mode

## Goal
Create a mirror effect by flipping the image horizontally.

## Main Hint
Use the `flip_image()` function with parameter `flip_code=1` to flip the image horizontally.

**flip_code values:**
- `0` = Flip vertically
- `1` = Flip horizontally ← Use this one!
- `-1` = Flip both ways

## Code Structure
```python
# 1. Initialize camera
# 2. In the loop:
#    - Get frame
#    - Flip image: flipped_frame = flip_image(camera_frame=..., flip_code=1)
#    - Display flipped image
# 3. Close camera
```

## Required Function:
- `flip_image(camera_frame=..., flip_code=1)` - Flip image

