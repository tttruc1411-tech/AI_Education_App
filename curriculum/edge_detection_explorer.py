# TITLE: Edge Detection Explorer
# TITLE_VI: Khám Phá Phát Hiện Cạnh
# LEVEL: Beginner
# ICON: 🔍
# COLOR: #22c55e
# DESC: Discover edges in images.
# DESC_VI: Khám phá các cạnh trong hình ảnh.
# ORDER: 12
# ============================================================



import camera
import display
import image
import variables

# Step 1: Create threshold variables (try changing these!)
# Lower threshold — controls weak edge sensitivity
threshold1 = variables.Create_Number(value = 100)
# Upper threshold — controls strong edge detection
threshold2 = variables.Create_Number(value = 200)

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Edge Detection Explorer ready!")

# Step 3: Detect edges on every frame
while True:
    # Grab a frame from the camera
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Find edges using the Canny algorithm
    edge_map = image.detect_edges(input_image = camera_frame, threshold1 = threshold1, threshold2 = threshold2)

    # Show the edge map (white = edges, black = background)
    display.Show_Image(camera_frame = edge_map)

    # Display the threshold values in the Results panel
    display.Observe_Variable(var_name = 'Threshold 1', var_value = threshold1)
    display.Observe_Variable(var_name = 'Threshold 2', var_value = threshold2)

# Clean up
camera.Close_Camera(capture_camera = capture_camera)
