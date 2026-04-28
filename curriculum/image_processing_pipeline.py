# TITLE: Image Processing Pipeline
# TITLE_VI: Chuỗi Xử Lý Hình Ảnh
# LEVEL: Intermediate
# ICON: 🔗
# COLOR: #eab308
# DESC: Chain multiple image effects together.
# DESC_VI: Kết hợp nhiều hiệu ứng hình ảnh với nhau.
# ORDER: 18
# ============================================================



import camera
import display
import image

# Step 1: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Image Processing Pipeline ready!")

# Step 2: Process each frame through a chain of effects
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Chain 1: Convert color image to grayscale
    gray = image.convert_to_gray(input_image = camera_frame)

    # Chain 2: Smooth the grayscale image with blur
    blurred = image.apply_blur(input_image = gray, kernel_size = 5)

    # Chain 3: Find edges in the blurred image
    edges = image.detect_edges(input_image = blurred, threshold1 = 50, threshold2 = 150)

    # Chain 4: Brighten the edge map so it's easier to see
    result = image.adjust_brightness(input_image = edges, factor = 1.5)

    # Stream the final processed image
    display.Show_Image(camera_frame = result)
    display.Observe_Variable(var_name = 'Pipeline Steps', var_value = 4)

camera.Close_Camera(capture_camera = capture_camera)
