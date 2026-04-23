# TITLE: Repeat Capture Series
# TITLE_VI: Chụp Ảnh Liên Tục
# LEVEL: Intermediate
# ICON: 📸
# COLOR: #eab308
# DESC: Capture a series of photos automatically.
# DESC_VI: Tự động chụp một loạt ảnh liên tiếp.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera, Save_Frame
# Import image processing blocks
from src.modules.library.functions.image_processing import adjust_brightness, draw_text
# Import display blocks
from src.modules.library.functions.display_blocks import Show_Image

# Step 1: Start the camera
capture_camera = Init_Camera()
print("[OK] Repeat Capture Series ready!")

# Step 2: Capture 5 photos in a loop with brightness and labels
for i in range(5):
    # Grab a frame from the camera
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Slightly brighten each frame
    camera_frame = adjust_brightness(input_image = camera_frame, factor = 1.2)

    # Add a frame counter label to the image
    camera_frame = draw_text(input_image = camera_frame, text = f'Frame {i + 1}', x = 10, y = 30)

    # Show the labeled frame
    Show_Image(camera_frame = camera_frame)

    # Save each frame with a sequential filename
    Save_Frame(camera_frame = camera_frame, file_path = f'capture_{i + 1}.jpg')
    print(f"Saved frame {i + 1} of 5")

# Step 3: Clean up
Close_Camera(capture_camera = capture_camera)
print("[OK] All 5 photos captured!")
