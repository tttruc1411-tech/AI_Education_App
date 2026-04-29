# Lesson 2 - Step 5: Filter Chain
## Nhiệm vụ / Task
Kết hợp nhiều bộ lọc với nhau.

## Hướng dẫn / Instructions
1. Khởi tạo camera
2. Trong vòng lặp, lấy khung hình
3. Chuyển ảnh sang màu xám
4. Làm mờ ảnh xám
5. Phát hiện cạnh trên ảnh đã làm mờ
6. Hiển thị kết quả cuối cùng
7. Đóng camera

## Functions cần dùng
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình
- `convert_to_gray(input_image)` - Chuyển màu xám
- `apply_blur(input_image, kernel_size)` - Làm mờ
- `detect_edges(input_image, threshold1, threshold2)` - Phát hiện cạnh
- `Show_Image(camera_frame)` - Hiển thị ảnh
- `Close_Camera(capture_camera)` - Đóng camera

## Gợi ý
- Kết quả của bộ lọc này là đầu vào của bộ lọc tiếp theo
- Thứ tự các bộ lọc rất quan trọng
- Làm mờ trước khi phát hiện cạnh giúp giảm nhiễu
