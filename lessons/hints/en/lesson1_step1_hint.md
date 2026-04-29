# 💡 Hint: My First Camera

## Step 1: Initialize Camera
You need to use the `Init_Camera()` function to start the camera. This function returns a camera object that you need to save to a variable.

**Hint:**
```python
capture_camera = Init_Camera()
```

## Step 2: Get Frame
Inside the `while True` loop, use the `Get_Camera_Frame()` function to get each frame from the camera.

**Hint:**
- Pass the `capture_camera` parameter to the function
- Save the result to the `camera_frame` variable

## Step 3: Display Image
Use the `Show_Image()` function to display the frame on the screen.

**Hint:**
- Pass the `camera_frame` parameter to the function

## Step 4: Close Camera
After the loop, use the `Close_Camera()` function to properly close the camera.

**Hint:**
- Pass the `capture_camera` parameter to the function

## Required Functions:
- `Init_Camera()` - Initialize camera
- `Get_Camera_Frame(capture_camera=...)` - Get frame
- `Show_Image(camera_frame=...)` - Display image
- `Close_Camera(capture_camera=...)` - Close camera

