# 💡 Hint: Brightness Control

## Goal
Adjust the brightness of the image.

## Main Hint
Use the `adjust_brightness()` function with parameter `brightness_value`.

**Brightness values:**
- `< 0` = Darker
- `0` = No change
- `> 0` = Brighter
- Example: `50` = Increase brightness by 50 units

## Code Structure
```python
# 1. Initialize camera
# 2. In the loop:
#    - Get frame
#    - Adjust brightness: bright_frame = adjust_brightness(camera_frame=..., brightness_value=50)
#    - Display adjusted image
# 3. Close camera
```

## Required Function:
- `adjust_brightness(camera_frame=..., brightness_value=...)` - Adjust brightness

