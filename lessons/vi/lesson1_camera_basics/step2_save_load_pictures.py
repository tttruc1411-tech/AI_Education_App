# ============================================================
# LESSON 1: Camera Basics - Step 2
# TITLE: Save & Load Pictures
# TITLE_VI: Lưu Và Tải Ảnh
# ============================================================

# Import camera và display modules
import camera
import display

# Bước 1: Khởi tạo camera
# __BLANK__ capture_camera = camera.Init_Camera()

# Bước 2: Chụp một khung hình
# __BLANK__ camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

# Bước 3: Lưu khung hình
# __BLANK__ camera.Save_Frame(camera_frame = camera_frame, file_path = 'my_photo.jpg')

# Bước 4: Đóng camera
# __BLANK__ camera.Close_Camera(capture_camera = capture_camera)

# Bước 5: Tải ảnh đã lưu
# __BLANK__ loaded_image = camera.Load_Image(file_path = 'my_photo.jpg')

# Bước 6: Hiển thị ảnh đã tải
# __BLANK__ display.Show_Image(camera_frame = loaded_image)

print("[OK] Photo saved and loaded!")
