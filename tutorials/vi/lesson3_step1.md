# Lesson 3 - Step 1: Draw Rectangle
## Nhiệm vụ / Task
Vẽ hình chữ nhật lên hình ảnh camera.

## Hướng dẫn / Instructions
1. Khởi tạo camera
2. Trong vòng lặp, lấy khung hình
3. Sử dụng `Draw_Rectangle()` với `x=100`, `y=100`, `width=200`, `height=150`, `color="green"`
4. Hiển thị ảnh có hình chữ nhật
5. Đóng camera

## Functions cần dùng
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình
- `Draw_Rectangle(camera_frame, x, y, width, height, color)` - Vẽ hình chữ nhật
- `Show_Image(camera_frame)` - Hiển thị ảnh
- `Close_Camera(capture_camera)` - Đóng camera

## Gợi ý
- `x, y` là tọa độ góc trên trái của hình chữ nhật
- `width, height` là chiều rộng và chiều cao
- Màu có sẵn: "green", "red", "blue", "yellow", "white"
