# TITLE: Side-by-Side Filters
# TITLE_VI: So Sánh Bộ Lọc
# LEVEL: Intermediate
# ICON: 🔀
# COLOR: #eab308
# DESC: Compare original and filtered images side by side.
# DESC_VI: So sánh hình ảnh gốc và đã lọc cạnh nhau.
# ORDER: 45
# ============================================================



import camera
import display
import image

# Step 1: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Side-by-Side Filters ready!")

# Step 2: Apply edge detection and compare with the original
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Convert the frame to grayscale for edge detection
    gray = image.convert_to_gray(input_image = camera_frame)

    # Apply edge detection to find outlines in the image
    edges = image.detect_edges(input_image = gray, threshold1 = 100, threshold2 = 200)

    # Stack the original and filtered images side by side for comparison
    combined = display.Stack_Images(image1 = camera_frame, image2 = edges, direction = 'horizontal')

    # Show the combined side-by-side result
    display.Show_Image(camera_frame = combined)
    display.Observe_Variable(var_name = 'Filter', var_value = 'Edge Detection')

camera.Close_Camera(capture_camera = capture_camera)
