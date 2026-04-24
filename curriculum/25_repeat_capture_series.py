# TITLE: Repeat Capture Series
# TITLE_VI: Chụp Ảnh Liên Tục
# LEVEL: Intermediate
# ICON: 📸
# COLOR: #eab308
# DESC: Capture a series of photos automatically.
# DESC_VI: Tự động chụp một loạt ảnh liên tiếp.
# ============================================================



import camera
import display
import image

# Step 1: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Repeat Capture Series ready!")

# Step 2: Capture 5 photos in a loop with brightness and labels
for i in range(5):
    # Grab a frame from the camera
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Slightly brighten each frame
    camera_frame = image.adjust_brightness(input_image = camera_frame, factor = 1.2)

    # Add a frame counter label to the image
    camera_frame = image.draw_text(input_image = camera_frame, text = f'Frame {i + 1}', x = 10, y = 30)

    # Show the labeled frame
    display.Show_Image(camera_frame = camera_frame)

    # Save each frame with a sequential filename
    camera.Save_Frame(camera_frame = camera_frame, file_path = f'capture_{i + 1}.jpg')
    print(f"Saved frame {i + 1} of 5")

# Step 3: Clean up
camera.Close_Camera(capture_camera = capture_camera)
print("[OK] All 5 photos captured!")
