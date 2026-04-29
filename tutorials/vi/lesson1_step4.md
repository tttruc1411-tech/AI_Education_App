# Lesson 1 - Step 4: Brightness Control
## Nhiệm vụ / Task
Điều chỉnh độ sáng của hình ảnh camera.

## Hướng dẫn / Instructions
1. Khởi tạo camera
2. Trong vòng lặp, lấy khung hình
3. Sử dụng `adjust_brightness()` với `factor=1.5` để tăng độ sáng
4. Hiển thị ảnh đã điều chỉnh
5. Đóng camera

## Functions cần dùng
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình
- `adjust_brightness(input_image, factor)` - Điều chỉnh độ sáng
- `Show_Image(camera_frame)` - Hiển thị ảnh
- `Close_Camera(capture_camera)` - Đóng camera

## Gợi ý
- `factor > 1.0` để tăng độ sáng (ví dụ: 1.5 = tăng 50%)
- `factor < 1.0` để giảm độ sáng (ví dụ: 0.5 = giảm 50%)
- `factor = 1.0` để giữ nguyên
