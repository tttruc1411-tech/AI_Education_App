# TITLE: Photo Crop & Frame
# TITLE_VI: Cắt & Khung Ảnh
# LEVEL: Beginner
# ICON: ✂️
# COLOR: #22c55e
# DESC: Crop regions from your camera feed.
# DESC_VI: Cắt vùng ảnh từ camera của bạn.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import crop function
from src.modules.library.functions.image_processing import crop_image
# Import variable blocks to define the crop area
from src.modules.library.functions.variables import Create_Number
# Import display block
from src.modules.library.functions.display_blocks import Show_Image

# Step 1: Define the crop region (try changing these values!)
x = Create_Number(value = 100)       # Left edge of crop
y = Create_Number(value = 80)        # Top edge of crop
width = Create_Number(value = 200)   # Width of crop area
height = Create_Number(value = 200)  # Height of crop area

# Step 2: Start the camera
capture_camera = Init_Camera()
print("[OK] Photo Crop & Frame ready!")

# Step 3: Crop every frame
while True:
    # Grab a frame from the camera
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Crop a rectangular region from the frame
    cropped = crop_image(input_image = camera_frame, x = x, y = y, width = width, height = height)

    # Show the cropped region
    Show_Image(camera_frame = cropped)

# Clean up
Close_Camera(capture_camera = capture_camera)
