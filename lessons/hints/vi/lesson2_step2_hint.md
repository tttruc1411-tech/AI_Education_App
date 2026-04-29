# 💡 Gợi Ý - Hint: Blur Effect

## Mục Tiêu
Làm mờ ảnh (blur effect).

## Gợi Ý Chính
Sử dụng hàm `apply_blur()` với tham số `blur_amount`.

**Giá trị blur_amount:**
- Phải là số lẻ (odd number): 3, 5, 7, 9, 11, ...
- Số càng lớn = Mờ càng nhiều
- Khuyến nghị: Bắt đầu với `blur_amount=15`

## Cấu Trúc Code
```python
# 1. Khởi tạo camera
# 2. Trong vòng lặp:
#    - Lấy khung hình
#    - Làm mờ: blurred_frame = apply_blur(camera_frame=..., blur_amount=15)
#    - Hiển thị ảnh mờ
# 3. Đóng camera
```

## Hàm Cần Dùng:
- `apply_blur(camera_frame=..., blur_amount=...)` - Làm mờ ảnh
