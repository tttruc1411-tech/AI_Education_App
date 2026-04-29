# Lesson 2 - Step 4: Resize Image
## Nhiệm vụ / Task
Thay đổi kích thước hình ảnh camera.

## Hướng dẫn / Instructions
1. Khởi tạo camera
2. Trong vòng lặp, lấy khung hình
3. Sử dụng `resize_image()` với `width=320`, `height=240` để thu nhỏ ảnh
4. Hiển thị ảnh đã thay đổi kích thước
5. Đóng camera

## Functions cần dùng
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình
- `resize_image(input_image, width, height)` - Thay đổi kích thước
- `Show_Image(camera_frame)` - Hiển thị ảnh
- `Close_Camera(capture_camera)` - Đóng camera

## Gợi ý
- Thu nhỏ ảnh giúp xử lý nhanh hơn
- Phóng to ảnh có thể làm giảm chất lượng
- Kích thước phổ biến: 320x240, 640x480, 1280x720
