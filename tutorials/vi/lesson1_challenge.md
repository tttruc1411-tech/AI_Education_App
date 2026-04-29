# Lesson 1 - Challenge: Smart Photo Booth
## Thách thức / Challenge
Tạo một gian hàng chụp ảnh với hiệu ứng gương và tự động chụp ảnh.

## Yêu cầu / Requirements
1. Khởi tạo camera
2. Hiển thị video với hiệu ứng gương (lật ngang)
3. Sau 3 giây (khoảng 90 khung hình), tự động chụp và lưu ảnh
4. Lưu ảnh với tên "photo_booth_1.jpg"
5. Tiếp tục hiển thị video
6. Đóng camera khi kết thúc

## Gợi ý
- Sử dụng biến đếm `frame_count` để đếm số khung hình
- Mỗi lần lặp, tăng `frame_count` lên 1
- Khi `frame_count == 90`, gọi `Save_Frame()` để lưu ảnh
- Reset `frame_count = 0` sau khi chụp để có thể chụp tiếp

## Functions cần dùng
- `Init_Camera()`, `Get_Camera_Frame()`, `Close_Camera()`
- `flip_image(input_image, direction="horizontal")`
- `Save_Frame(camera_frame, file_path)`
- `Show_Image(camera_frame)`

## Mục tiêu học tập
Kết hợp nhiều kỹ năng: lật ảnh, đếm khung hình, lưu ảnh tự động.
