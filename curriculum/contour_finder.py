# TITLE: Contour Finder
# TITLE_VI: Tìm Đường Viền
# LEVEL: Beginner
# ICON: ✏️
# COLOR: #22c55e
# DESC: Find and draw object outlines using thresholding and contours.
# DESC_VI: Tìm và vẽ đường viền đối tượng bằng ngưỡng và contour.
# ORDER: 42
# ============================================================



import camera
import display
import image
import variables

# Step 1: Create a threshold cutoff variable
# This controls how sensitive the contour detection is
# Lower values detect more contours, higher values detect fewer
cutoff = variables.Create_Number(value = 100)

# Step 2: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Contour Finder ready!")

# Step 3: Detect contours on every frame
while True:
    # Grab a frame from the camera
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # First, convert to black & white using threshold
    # This creates a clean mask for contour detection
    thresh_image = image.threshold_image(input_image = camera_frame, threshold = cutoff)

    # Now detect contours (outlines) on the thresholded image
    # Green lines will be drawn around each detected shape
    contour_image = image.detect_contours(input_image = thresh_image)

    # Show the contour result in the Live Feed
    display.Show_Image(camera_frame = contour_image)

    # Display the current threshold cutoff in the Results panel
    display.Observe_Variable(var_name = 'Cutoff', var_value = cutoff)

# Clean up
camera.Close_Camera(capture_camera = capture_camera)
