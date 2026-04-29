# 💡 Gợi Ý - Hint: Filter Chain

## Mục Tiêu
Kết hợp nhiều bộ lọc (filters) với nhau.

## Gợi Ý Chính
Áp dụng nhiều hiệu ứng lần lượt lên cùng một ảnh.

**Ví dụ chuỗi filters:**
1. Chuyển sang xám
2. Làm mờ
3. Phát hiện cạnh

## Cấu Trúc Code
```python
# 1. Khởi tạo camera
# 2. Trong vòng lặp:
#    - Lấy khung hình
#    - Filter 1: gray = convert_to_gray(camera_frame=...)
#    - Filter 2: blurred = apply_blur(camera_frame=gray, blur_amount=15)
#    - Filter 3: edges = detect_edges(camera_frame=blurred)
#    - Hiển thị kết quả cuối
# 3. Đóng camera
```

## Lưu Ý:
- Kết quả của filter trước là input của filter sau
- Thứ tự filters ảnh hưởng đến kết quả cuối

## Hàm Cần Dùng:
- `convert_to_gray()` - Xám
- `apply_blur()` - Mờ
- `detect_edges()` - Cạnh
