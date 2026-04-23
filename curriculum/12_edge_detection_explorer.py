# TITLE: Edge Detection Explorer
# TITLE_VI: Khám Phá Phát Hiện Cạnh
# LEVEL: Beginner
# ICON: 🔍
# COLOR: #22c55e
# DESC: Discover edges in images.
# DESC_VI: Khám phá các cạnh trong hình ảnh.
# ============================================================

# Import camera blocks
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import edge detection function
from src.modules.library.functions.image_processing import detect_edges
# Import variable blocks to control thresholds
from src.modules.library.functions.variables import Create_Number
# Import display blocks
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable

# Step 1: Create threshold variables (try changing these!)
# Lower threshold — controls weak edge sensitivity
threshold1 = Create_Number(value = 100)
# Upper threshold — controls strong edge detection
threshold2 = Create_Number(value = 200)

# Step 2: Start the camera
capture_camera = Init_Camera()
print("[OK] Edge Detection Explorer ready!")

# Step 3: Detect edges on every frame
while True:
    # Grab a frame from the camera
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # Find edges using the Canny algorithm
    edge_map = detect_edges(input_image = camera_frame, threshold1 = threshold1, threshold2 = threshold2)

    # Show the edge map (white = edges, black = background)
    Show_Image(camera_frame = edge_map)

    # Display the threshold values in the Results panel
    Observe_Variable(var_name = 'Threshold 1', var_value = threshold1)
    Observe_Variable(var_name = 'Threshold 2', var_value = threshold2)

# Clean up
Close_Camera(capture_camera = capture_camera)
