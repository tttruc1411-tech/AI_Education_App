# Lesson 3 - Step 3: Multiple Shapes
## Nhiệm vụ / Task
Vẽ nhiều hình dạng khác nhau trên cùng một ảnh.

## Hướng dẫn / Instructions
1. Khởi tạo camera
2. Trong vòng lặp, lấy khung hình
3. Vẽ một hình chữ nhật màu xanh lá
4. Vẽ một hình tròn màu đỏ
5. Vẽ thêm một hình chữ nhật màu vàng
6. Hiển thị ảnh với tất cả các hình
7. Đóng camera

## Functions cần dùng
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình
- `Draw_Rectangle(camera_frame, x, y, width, height, color)` - Vẽ hình chữ nhật
- `Draw_Circle(camera_frame, center_x, center_y, radius, color)` - Vẽ hình tròn
- `Show_Image(camera_frame)` - Hiển thị ảnh
- `Close_Camera(capture_camera)` - Đóng camera

## Gợi ý
- Vẽ lần lượt từng hình lên cùng một frame
- Chọn vị trí sao cho các hình không chồng lên nhau
