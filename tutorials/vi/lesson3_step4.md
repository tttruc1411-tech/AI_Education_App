# Lesson 3 - Step 4: Color Variations
## Nhiệm vụ / Task
Thử nghiệm với các màu sắc khác nhau.

## Hướng dẫn / Instructions
1. Khởi tạo camera
2. Trong vòng lặp, lấy khung hình
3. Vẽ 4 hình tròn với các màu khác nhau: green, red, blue, yellow
4. Mỗi hình tròn ở một vị trí khác nhau
5. Hiển thị ảnh
6. Đóng camera

## Functions cần dùng
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình
- `Draw_Circle(camera_frame, center_x, center_y, radius, color)` - Vẽ hình tròn
- `Show_Image(camera_frame)` - Hiển thị ảnh
- `Close_Camera(capture_camera)` - Đóng camera

## Gợi ý
- Màu có sẵn: "green", "red", "blue", "yellow", "white"
- Đặt 4 hình tròn ở 4 góc màn hình
- Ví dụ vị trí: (100, 100), (540, 100), (100, 380), (540, 380)
