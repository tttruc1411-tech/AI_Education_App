# TITLE: Image Blender
# TITLE_VI: Trộn Hình Ảnh
# LEVEL: Beginner
# ICON: 🎨
# COLOR: #22c55e
# DESC: Blend your camera feed with a loaded image.
# DESC_VI: Trộn hình ảnh camera với một hình ảnh đã tải.
# ORDER: 40
# ============================================================



import camera
import display
import image
import variables

# Step 1: Load an overlay image from file
# This image will be blended on top of the camera feed
overlay = camera.Load_Image(file_path = 'my_photo.jpg')

# Step 2: Create a blend factor variable (0.0 to 1.0)
# 0.0 = only camera, 1.0 = only overlay, 0.5 = equal mix
alpha = variables.Create_Decimal(value = 0.5)

# Step 3: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Image Blender ready!")

# Step 4: Blend the camera feed with the overlay on every frame
while True:
    # Grab a frame from the camera
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Blend the camera frame with the overlay image
    # The alpha value controls how much of each image you see
    blended = image.blend_images(image1 = camera_frame, image2 = overlay, alpha = alpha)

    # Show the blended result in the Live Feed
    display.Show_Image(camera_frame = blended)

    # Display the current blend factor in the Results panel
    display.Observe_Variable(var_name = 'Alpha', var_value = alpha)

# Clean up
camera.Close_Camera(capture_camera = capture_camera)
