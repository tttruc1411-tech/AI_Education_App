# TITLE: Channel Splitter
# TITLE_VI: Tách Kênh Màu
# LEVEL: Beginner
# ICON: 🌈
# COLOR: #22c55e
# DESC: Split your camera image into Blue, Green, and Red channels.
# DESC_VI: Tách hình ảnh camera thành các kênh Xanh dương, Xanh lá và Đỏ.
# ORDER: 41
# ============================================================



import camera
import display
import image

# Step 1: Start the camera
capture_camera = camera.Init_Camera()
print("[OK] Channel Splitter ready!")

# Step 2: Split and display channels on every frame
while True:
    # Grab a color frame from the camera
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Split the image into its 3 color channels: Blue, Green, Red
    # Each channel is a grayscale image showing that color's intensity
    channels = image.split_channels(input_image = camera_frame)

    # channels[0] = Blue, channels[1] = Green, channels[2] = Red
    blue_channel = channels[0]
    green_channel = channels[1]
    red_channel = channels[2]

    # Stack the Blue and Green channels side by side
    top_row = display.Stack_Images(image1 = blue_channel, image2 = green_channel, direction = 'horizontal')

    # Stack that result with the Red channel below
    # First stack Red with the original frame for a 2x2 grid
    bottom_row = display.Stack_Images(image1 = red_channel, image2 = camera_frame, direction = 'horizontal')

    # Combine top and bottom rows vertically
    grid = display.Stack_Images(image1 = top_row, image2 = bottom_row, direction = 'vertical')

    # Show the 2x2 grid: Blue | Green / Red | Original
    display.Show_Image(camera_frame = grid)

# Clean up
camera.Close_Camera(capture_camera = capture_camera)
