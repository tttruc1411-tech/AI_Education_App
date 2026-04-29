# Lessons Structure / Cấu Trúc Giáo Án

## Overview / Tổng Quan
Folder này chứa các bài học (lessons) được thiết kế cho học viên. Mỗi lesson bao gồm nhiều steps và một challenge cuối cùng.

## Lesson Structure / Cấu Trúc Bài Học

### Lesson 1: Camera Basics (Cơ Bản Về Camera)
**Mục tiêu**: Học cách làm việc với camera và hiển thị hình ảnh

**Steps**:
1. `step1_my_first_camera.py` - Khởi tạo camera và hiển thị video
2. `step2_save_load_pictures.py` - Lưu và tải ảnh
3. `step3_mirror_selfie_mode.py` - Chế độ selfie gương
4. `step4_brightness_control.py` - Điều chỉnh độ sáng
5. `step5_rotate_image.py` - Xoay ảnh

**Challenge**: `challenge_photo_booth.py` - Gian hàng chụp ảnh thông minh

---

### Lesson 2: Image Processing (Xử Lý Hình Ảnh)
**Mục tiêu**: Làm chủ các bộ lọc và biến đổi hình ảnh

**Steps**:
1. `step1_image_filters_lab.py` - Bộ lọc màu xám
2. `step2_blur_effect.py` - Hiệu ứng làm mờ
3. `step3_edge_detection.py` - Phát hiện cạnh
4. `step4_resize_image.py` - Thay đổi kích thước
5. `step5_filter_chain.py` - Kết hợp nhiều bộ lọc

**Challenge**: `challenge_artistic_filter.py` - Chuỗi bộ lọc nghệ thuật

---

### Lesson 3: Drawing & Shapes (Vẽ & Hình Dạng)
**Mục tiêu**: Học cách vẽ hình và chữ lên ảnh

**Steps**:
1. `step1_draw_rectangle.py` - Vẽ hình chữ nhật
2. `step2_draw_circle.py` - Vẽ hình tròn
3. `step3_multiple_shapes.py` - Vẽ nhiều hình dạng
4. `step4_color_variations.py` - Biến thể màu sắc

**Challenge**: `challenge_creative_art.py` - Vẽ tranh sáng tạo (ngôi nhà)

---

## File Format / Định Dạng File

Mỗi file step có cấu trúc:
```python
# ============================================================
# LESSON X: [Lesson Name] - Step Y
# TITLE: [English Title]
# TITLE_VI: [Vietnamese Title]
# ============================================================
# NHIỆM VỤ: [Vietnamese Task]
# TASK: [English Task]
# ============================================================

# Import statements
from src.modules.library.functions...

# ============================================================
# HƯỚNG DẪN / INSTRUCTIONS:
# [Detailed step-by-step instructions]
# ============================================================

# TODO: Code sections for students to complete
```

## Available Functions / Các Hàm Có Sẵn

### Camera Functions (ai_blocks.py)
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera)` - Lấy khung hình
- `Close_Camera(capture_camera)` - Đóng camera
- `Save_Frame(camera_frame, file_path)` - Lưu ảnh
- `Load_Image(file_path)` - Tải ảnh

### Image Processing Functions (image_processing.py)
- `convert_to_gray(input_image)` - Chuyển sang màu xám
- `apply_blur(input_image, kernel_size)` - Làm mờ ảnh
- `detect_edges(input_image, threshold1, threshold2)` - Phát hiện cạnh
- `flip_image(input_image, direction)` - Lật ảnh
- `resize_image(input_image, width, height)` - Thay đổi kích thước
- `rotate_image(input_image, angle)` - Xoay ảnh
- `adjust_brightness(input_image, brightness_value)` - Điều chỉnh độ sáng

### Display Functions (display_blocks.py)
- `Show_Image(camera_frame)` - Hiển thị ảnh
- `Draw_Rectangle(camera_frame, x, y, width, height, color)` - Vẽ hình chữ nhật
- `Draw_Circle(camera_frame, center_x, center_y, radius, color)` - Vẽ hình tròn
- `Show_FPS(camera_frame)` - Hiển thị FPS
- `Observe_Variable(var_name, var_value)` - Quan sát biến

### Available Colors / Màu Có Sẵn
- `"green"` - Xanh lá
- `"red"` - Đỏ
- `"blue"` - Xanh dương
- `"yellow"` - Vàng
- `"white"` - Trắng

---

## Teaching Philosophy / Triết Lý Giảng Dạy

1. **Học qua thực hành**: Học viên tự viết code, không copy-paste
2. **Từng bước một**: Mỗi step tập trung vào một kỹ năng cụ thể
3. **Hướng dẫn rõ ràng**: TODO comments chỉ rõ cần làm gì
4. **Challenge cuối**: Kết hợp tất cả kiến thức đã học
5. **Song ngữ**: Hỗ trợ cả tiếng Việt và tiếng Anh

---

## Notes for Teachers / Ghi Chú Cho Giáo Viên

- Mỗi step nên mất 5-10 phút để hoàn thành
- Challenge nên mất 15-20 phút
- Khuyến khích học viên thử nghiệm với các tham số khác nhau
- Giải thích ý nghĩa của từng function trước khi học viên sử dụng
- Cho phép học viên sáng tạo trong challenge

---

## Future Lessons / Bài Học Tương Lai

Các lesson tiếp theo sẽ bao gồm:
- Lesson 4: Color Science (Khoa học Màu sắc)
- Lesson 5: Face Detection AI (AI Phát hiện Khuôn mặt)
- Lesson 6: Object Detection AI (AI Phát hiện Vật thể)
- Lesson 7: AI Applications (Ứng dụng AI)
- Lesson 8: Performance & Monitoring (Hiệu suất & Giám sát)
