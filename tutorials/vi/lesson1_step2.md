# Lesson 1 - Step 2: Save & Load Pictures
## Nhiệm vụ / Task
Chụp ảnh từ camera và lưu vào ổ đĩa, sau đó tải lại.

## Hướng dẫn / Instructions
1. Khởi tạo camera
2. Lấy một khung hình từ camera
3. Sử dụng `Save_Frame()` để lưu ảnh với tên "my_photo.jpg"
4. Sử dụng `Load_Image()` để tải ảnh vừa lưu
5. Hiển thị ảnh đã tải
6. Đóng camera

## Functions cần dùng
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình
- `Save_Frame(camera_frame, file_path)` - Lưu ảnh
- `Load_Image(file_path)` - Tải ảnh từ ổ đĩa
- `Show_Image(camera_frame)` - Hiển thị ảnh
- `Close_Camera(capture_camera)` - Đóng camera

## Gợi ý
- Ảnh sẽ được lưu vào folder `projects/data/saved/`
- Tên file có thể là "my_photo.jpg" hoặc bất kỳ tên nào bạn muốn
