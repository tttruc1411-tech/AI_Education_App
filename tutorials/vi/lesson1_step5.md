# Lesson 1 - Step 5: Rotate Image
## Nhiệm vụ / Task
Xoay hình ảnh camera 90 độ.

## Hướng dẫn / Instructions
1. Khởi tạo camera
2. Trong vòng lặp, lấy khung hình
3. Sử dụng `rotate_image()` với `angle=90` để xoay ảnh
4. Hiển thị ảnh đã xoay
5. Đóng camera

## Functions cần dùng
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình
- `rotate_image(input_image, angle)` - Xoay ảnh
- `Show_Image(camera_frame)` - Hiển thị ảnh
- `Close_Camera(capture_camera)` - Đóng camera

## Gợi ý
- `angle=90` để xoay 90 độ ngược chiều kim đồng hồ
- `angle=180` để xoay 180 độ (lật ngược)
- `angle=270` để xoay 270 độ (hoặc -90 độ)
