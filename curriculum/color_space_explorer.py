# TITLE: Color Space Explorer
# TITLE_VI: Khám Phá Không Gian Màu
# LEVEL: Beginner
# ICON: 🌈
# COLOR: #22c55e
# DESC: Explore how computers see colors.
# DESC_VI: Khám phá cách máy tính nhìn thấy màu sắc.
# ORDER: 13
# ============================================================



import camera
import display
import image

# Step 1: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Color Space Explorer ready!")

# Step 2: Show both BGR and HSV views
while True:
    # Grab a frame from the camera (this is in BGR color format)
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Convert the BGR image to HSV (Hue, Saturation, Value)
    # HSV separates color info (Hue) from brightness (Value)
    hsv_image = image.convert_to_hsv(input_image = camera_frame)

    # Show the original BGR image
    display.Show_Image(camera_frame = camera_frame)

    # Show the HSV version — notice how colors look different!
    display.Show_Image(camera_frame = hsv_image)

# Clean up
camera.Close_Camera(capture_camera = capture_camera)
