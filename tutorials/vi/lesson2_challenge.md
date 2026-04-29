# Lesson 2 - Challenge: Artistic Filter Pipeline
## Thách thức / Challenge
Tạo một bộ lọc nghệ thuật độc đáo.

## Yêu cầu / Requirements
Tạo một hiệu ứng nghệ thuật bằng cách kết hợp ít nhất 3 bộ lọc:
1. Khởi tạo camera
2. Áp dụng chuỗi bộ lọc theo thứ tự:
   - Chuyển sang màu xám
   - Làm mờ với `kernel_size=7`
   - Phát hiện cạnh với `threshold1=50`, `threshold2=150`
   - Lật ảnh theo chiều ngang
3. Hiển thị kết quả
4. Đóng camera khi kết thúc

## Functions cần dùng
- `Init_Camera()`, `Get_Camera_Frame()`, `Close_Camera()`
- `convert_to_gray(input_image)`
- `apply_blur(input_image, kernel_size)`
- `detect_edges(input_image, threshold1, threshold2)`
- `flip_image(input_image, direction)`
- `Show_Image(camera_frame)`

## Mục tiêu học tập
Kết hợp tất cả kỹ năng xử lý ảnh đã học để tạo hiệu ứng nghệ thuật.

## Gợi ý
- Thử thay đổi các tham số để tạo hiệu ứng khác nhau
- Có thể thêm hoặc bỏ bớt bộ lọc để sáng tạo
