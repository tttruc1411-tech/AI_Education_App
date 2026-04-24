# TITLE: Grayscale Converter
# TITLE_VI: Chuyển Đổi Ảnh Xám
# LEVEL: Beginner
# ICON: ⬛
# COLOR: #22c55e
# DESC: Convert colors to grayscale.
# DESC_VI: Chuyển đổi ảnh màu sang ảnh xám.
# ============================================================



import camera
import display
import image

# Step 1: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Grayscale Converter ready!")

# Step 2: Convert every frame to grayscale
while True:
    # Grab a color frame from the camera (BGR = Blue, Green, Red channels)
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Convert to grayscale — this combines all 3 color channels into 1
    # The formula is roughly: Gray = 0.299*Red + 0.587*Green + 0.114*Blue
    # Human eyes are most sensitive to green, so green has the highest weight!
    gray_image = image.convert_to_gray(input_image = camera_frame)

    # Show the grayscale result
    display.Show_Image(camera_frame = gray_image)

# Clean up
camera.Close_Camera(capture_camera = capture_camera)
