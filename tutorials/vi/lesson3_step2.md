# Lesson 3 - Step 2: Draw Circle
## Nhiệm vụ / Task
Vẽ hình tròn lên hình ảnh camera.

## Hướng dẫn / Instructions
1. Khởi tạo camera
2. Trong vòng lặp, lấy khung hình
3. Sử dụng `Draw_Circle()` với `center_x=320`, `center_y=240`, `radius=100`, `color="red"`
4. Hiển thị ảnh có hình tròn
5. Đóng camera

## Functions cần dùng
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình
- `Draw_Circle(camera_frame, center_x, center_y, radius, color)` - Vẽ hình tròn
- `Show_Image(camera_frame)` - Hiển thị ảnh
- `Close_Camera(capture_camera)` - Đóng camera

## Gợi ý
- `center_x, center_y` là tọa độ tâm của hình tròn
- `radius` là bán kính
- Màu có sẵn: "green", "red", "blue", "yellow", "white"
