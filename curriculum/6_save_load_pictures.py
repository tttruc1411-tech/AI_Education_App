# TITLE: Save & Load Pictures
# TITLE_VI: Lưu & Tải Hình Ảnh
# LEVEL: Beginner
# ICON: 💾
# COLOR: #22c55e
# DESC: Save photos and load them back.
# DESC_VI: Lưu ảnh chụp và tải lại chúng.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera, Save_Frame, Load_Image
# Import display block
from src.modules.library.functions.display_blocks import Show_Image

# Step 1: Start the camera
capture_camera = Init_Camera()
print("[OK] Camera ready!")

# Step 2: Capture one frame from the camera
camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

# Step 3: Save the frame to a file on disk
Save_Frame(camera_frame = camera_frame, file_path = 'my_photo.jpg')

# Step 4: We're done with the camera, close it
Close_Camera(capture_camera = capture_camera)

# Step 5: Load the saved picture back from disk
loaded_image = Load_Image(file_path = 'my_photo.jpg')

# Step 6: Display the loaded image
Show_Image(camera_frame = loaded_image)
print("[OK] Photo saved and loaded!")
