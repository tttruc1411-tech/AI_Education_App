# Lesson 1 - Step 1: My First Camera
## Nhiệm vụ / Task
Khởi tạo camera và hiển thị video trực tiếp.

## Hướng dẫn / Instructions
1. Sử dụng `Init_Camera()` để khởi tạo camera
2. Trong vòng lặp `while True`, sử dụng `Get_Camera_Frame()` để lấy khung hình
3. Sử dụng `Show_Image()` để hiển thị khung hình
4. Cuối cùng, sử dụng `Close_Camera()` để đóng camera

## Functions cần dùng
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình từ camera
- `Show_Image(camera_frame)` - Hiển thị khung hình
- `Close_Camera(capture_camera)` - Đóng camera

## Gợi ý
- Lưu kết quả của `Init_Camera()` vào biến `capture_camera`
- Vòng lặp `while True` sẽ chạy liên tục để hiển thị video
- Nhớ truyền đúng tham số cho mỗi function

