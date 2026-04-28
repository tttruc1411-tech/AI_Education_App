# TITLE: Image Filters Lab
# TITLE_VI: Phòng Thí Nghiệm Bộ Lọc Ảnh
# LEVEL: Beginner
# ICON: 🎨
# COLOR: #22c55e
# DESC: Apply cool filters to your camera feed.
# DESC_VI: Áp dụng các bộ lọc thú vị lên hình ảnh camera.
# ORDER: 5
# ============================================================



import camera
import display
import image

# Step 1: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Filters Lab ready!")

# Step 2: Apply a chain of filters in a loop
while True:
    # Grab a frame from the camera
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Filter 1: Convert color image to grayscale
    gray = image.convert_to_gray(input_image = camera_frame)

    # Filter 2: Blur the image to smooth it out
    blurred = image.apply_blur(input_image = gray, kernel_size = 5)

    # Filter 3: Find edges in the blurred image
    edges = image.detect_edges(input_image = blurred, threshold1 = 100, threshold2 = 200)

    # Filter 4: Flip the result horizontally for fun
    flipped = image.flip_image(input_image = edges, direction = 'horizontal')

    # Show the final filtered image
    display.Show_Image(camera_frame = flipped)

# Clean up
camera.Close_Camera(capture_camera = capture_camera)
