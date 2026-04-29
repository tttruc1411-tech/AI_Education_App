# Lesson 2 - Step 2: Blur Effect
## Nhiệm vụ / Task
Áp dụng hiệu ứng làm mờ lên hình ảnh.

## Hướng dẫn / Instructions
1. Khởi tạo camera
2. Trong vòng lặp, lấy khung hình
3. Sử dụng `apply_blur()` với `kernel_size=15` để làm mờ ảnh
4. Hiển thị ảnh đã làm mờ
5. Đóng camera

## Functions cần dùng
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình
- `apply_blur(input_image, kernel_size)` - Làm mờ ảnh
- `Show_Image(camera_frame)` - Hiển thị ảnh
- `Close_Camera(capture_camera)` - Đóng camera

## Gợi ý
- `kernel_size` càng lớn, ảnh càng mờ
- `kernel_size` phải là số lẻ (5, 7, 9, 11, 15, ...)
- Làm mờ giúp giảm nhiễu trong ảnh
