# 💡 Hint: Resize Image

## Goal
Resize images.

## Main Hint
Use the `resize_image()` function with parameters `width` and `height`.

**Example sizes:**
- `width=320, height=240` = Small
- `width=640, height=480` = Medium
- `width=1280, height=720` = Large (HD)

## Code Structure
```python
# 1. Initialize camera
# 2. In the loop:
#    - Get frame
#    - Resize: resized_frame = resize_image(camera_frame=..., width=320, height=240)
#    - Display resized image
# 3. Close camera
```

## Required Function:
- `resize_image(camera_frame=..., width=..., height=...)` - Resize image

