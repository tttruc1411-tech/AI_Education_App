# TITLE: Text Overlay Studio
# TITLE_VI: Phòng Thu Chữ Trên Ảnh
# LEVEL: Beginner
# ICON: ✏️
# COLOR: #22c55e
# DESC: Add custom text to your camera feed.
# DESC_VI: Thêm chữ tùy chỉnh lên hình ảnh camera.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import text drawing function
from src.modules.library.functions.image_processing import draw_text
# Import variable block to create a text message
from src.modules.library.functions.variables import Create_Text
# Import display block
from src.modules.library.functions.display_blocks import Show_Image

# Step 1: Create a text message variable (change this to say anything!)
message = Create_Text(value = 'Hello World!')

# Step 2: Start the camera
capture_camera = Init_Camera()
print("[OK] Text Overlay Studio ready!")

# Step 3: Draw text on every frame
while True:
    # Grab a frame from the camera
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Draw our message on the image at position (10, 30)
    labeled = draw_text(input_image = camera_frame, text = message, x = 10, y = 30)

    # Show the image with text overlay
    Show_Image(camera_frame = labeled)

# Clean up
Close_Camera(capture_camera = capture_camera)
