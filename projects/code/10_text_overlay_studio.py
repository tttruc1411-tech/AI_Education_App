# TITLE: Text Overlay Studio
# TITLE_VI: Phòng Thu Chữ Trên Ảnh
# LEVEL: Beginner
# ICON: ✏️
# COLOR: #22c55e
# DESC: Add custom text to your camera feed.
# DESC_VI: Thêm chữ tùy chỉnh lên hình ảnh camera.
# ============================================================



import camera
import display
import image
import variables

# Step 1: Create a text message variable (change this to say anything!)
message = variables.Create_Text(value = 'Hello World!')

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Text Overlay Studio ready!")

# Step 3: Draw text on every frame
while True:
    # Grab a frame from the camera
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Draw our message on the image at position (10, 30)
    labeled = image.draw_text(input_image = camera_frame, text = message, x = 10, y = 30)

    # Show the image with text overlay
    display.Show_Image(camera_frame = labeled)

# Clean up
camera.Close_Camera(capture_camera = capture_camera)
