# TITLE: Photo Crop & Frame
# TITLE_VI: Cắt & Khung Ảnh
# LEVEL: Beginner
# ICON: ✂️
# COLOR: #22c55e
# DESC: Crop regions from your camera feed.
# DESC_VI: Cắt vùng ảnh từ camera của bạn.
# ORDER: 14
# ============================================================



import camera
import display
import image
import variables

# Step 1: Define the crop region (try changing these values!)
x = variables.Create_Number(value = 100)       # Left edge of crop
y = variables.Create_Number(value = 80)        # Top edge of crop
width = variables.Create_Number(value = 200)   # Width of crop area
height = variables.Create_Number(value = 200)  # Height of crop area

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Photo Crop & Frame ready!")

# Step 3: Crop every frame
while True:
    # Grab a frame from the camera
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Crop a rectangular region from the frame
    cropped = image.crop_image(input_image = camera_frame, x = x, y = y, width = width, height = height)

    # Show the cropped region
    display.Show_Image(camera_frame = cropped)

# Clean up
camera.Close_Camera(capture_camera = capture_camera)
