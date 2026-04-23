# TITLE: Shape Drawing Canvas
# TITLE_VI: Vẽ Hình Trên Canvas
# LEVEL: Beginner
# ICON: 🔷
# COLOR: #22c55e
# DESC: Draw shapes on your camera feed.
# DESC_VI: Vẽ các hình dạng lên hình ảnh camera.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import shape drawing blocks
from src.modules.library.functions.display_blocks import Draw_Rectangle, Draw_Circle, Show_Image

# Step 1: Start the camera
capture_camera = Init_Camera()
print("[OK] Shape Drawing Canvas ready!")

# Step 2: Draw shapes on every frame
while True:
    # Grab a frame from the camera
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Draw a green rectangle at the top-left area
    camera_frame = Draw_Rectangle(camera_frame = camera_frame, x = 50, y = 50, width = 200, height = 150, color = 'green')

    # Draw a red circle in the center area
    camera_frame = Draw_Circle(camera_frame = camera_frame, center_x = 320, center_y = 240, radius = 80, color = 'red')

    # Draw a blue rectangle at the bottom
    camera_frame = Draw_Rectangle(camera_frame = camera_frame, x = 100, y = 350, width = 150, height = 80, color = 'blue')

    # Show the frame with all shapes drawn on it
    Show_Image(camera_frame = camera_frame)

# Clean up
Close_Camera(capture_camera = capture_camera)
