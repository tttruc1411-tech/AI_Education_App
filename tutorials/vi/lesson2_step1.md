# Lesson 2 - Step 1: Image Filters Lab
## Nhiệm vụ / Task
Áp dụng bộ lọc xám (grayscale) lên hình ảnh camera.

## Hướng dẫn / Instructions
1. Khởi tạo camera
2. Trong vòng lặp, lấy khung hình
3. Sử dụng `convert_to_gray()` để chuyển ảnh sang màu xám
4. Hiển thị ảnh đã chuyển đổi
5. Đóng camera

## Functions cần dùng
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình
- `convert_to_gray(input_image)` - Chuyển sang màu xám
- `Show_Image(camera_frame)` - Hiển thị ảnh
- `Close_Camera(capture_camera)` - Đóng camera

## Gợi ý
- Ảnh xám chỉ có 1 kênh màu thay vì 3 kênh (RGB)
- Ảnh xám thường được dùng để xử lý ảnh nhanh hơn
