# 💡 Hint: Save & Load Pictures

## Step 1: Initialize and Capture
Initialize the camera and get a frame to capture.

**Hint:**
```python
capture_camera = Init_Camera()
camera_frame = Get_Camera_Frame(capture_camera=capture_camera)
```

## Step 2: Save Image
Use the `Save_Frame()` function to save the frame to a file.

**Hint:**
- Parameter 1: `camera_frame` - the frame to save
- Parameter 2: `file_path` - filename (e.g., 'my_photo.jpg')

## Step 3: Close Camera
Close the camera after capturing.

## Step 4: Load Saved Image
Use the `Load_Image()` function to load the image from file.

**Hint:**
```python
loaded_image = Load_Image(file_path='my_photo.jpg')
```

## Step 5: Display Image
Display the loaded image on the screen.

## Required Functions:
- `Save_Frame(camera_frame=..., file_path=...)` - Save image
- `Load_Image(file_path=...)` - Load image

