# ============================================================
# LESSON 2: Image Processing - Step 5
# TITLE: Filter Chain
# TITLE_VI: Chuỗi Bộ Lọc
# ============================================================

# Import camera, image processing, and display modules
import camera
import image
import display

# Step 1: Start the camera
# __BLANK__ capture_camera = camera.Init_Camera()

print("[OK] Filter chain ready!")

# Step 2: Apply filter chain
while True:
    # __BLANK__ camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # __BLANK__ gray_frame = image.convert_to_gray(input_image = camera_frame)

    # __BLANK__ blurred_frame = image.apply_blur(input_image = gray_frame, kernel_size = 5)

    # __BLANK__ edges_frame = image.detect_edges(input_image = blurred_frame, threshold1 = 100, threshold2 = 200)

    # __BLANK__ display.Show_Image(camera_frame = edges_frame)

# Step 3: Clean up
# __BLANK__ camera.Close_Camera(capture_camera = capture_camera)
