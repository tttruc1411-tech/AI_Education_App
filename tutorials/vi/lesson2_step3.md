# Lesson 2 - Step 3: Edge Detection
## Nhiệm vụ / Task
Phát hiện các cạnh trong hình ảnh.

## Hướng dẫn / Instructions
1. Khởi tạo camera
2. Trong vòng lặp, lấy khung hình
3. Sử dụng `detect_edges()` với `threshold1=100`, `threshold2=200`
4. Hiển thị ảnh cạnh
5. Đóng camera

## Functions cần dùng
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình
- `detect_edges(input_image, threshold1, threshold2)` - Phát hiện cạnh
- `Show_Image(camera_frame)` - Hiển thị ảnh
- `Close_Camera(capture_camera)` - Đóng camera

## Gợi ý
- `threshold1` và `threshold2` điều chỉnh độ nhạy của phát hiện cạnh
- Giá trị thấp hơn = phát hiện nhiều cạnh hơn
- Giá trị cao hơn = chỉ phát hiện cạnh rõ nét
