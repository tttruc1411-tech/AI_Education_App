# Lesson 1 - Step 3: Mirror Selfie Mode
## Nhiệm vụ / Task
Lật hình ảnh camera theo chiều ngang như gương.

## Hướng dẫn / Instructions
1. Khởi tạo camera
2. Trong vòng lặp, lấy khung hình từ camera
3. Sử dụng `flip_image()` với `direction="horizontal"` để lật ảnh
4. Hiển thị ảnh đã lật
5. Đóng camera khi kết thúc

## Functions cần dùng
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình
- `flip_image(input_image, direction)` - Lật ảnh
- `Show_Image(camera_frame)` - Hiển thị ảnh
- `Close_Camera(capture_camera)` - Đóng camera

## Gợi ý
- `direction="horizontal"` để lật ngang (như gương)
- `direction="vertical"` để lật dọc
- `direction="both"` để lật cả hai chiều
