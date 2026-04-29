# 💡 Gợi Ý - Hint: Rotate Image

## Mục Tiêu
Xoay ảnh 90 độ.

## Gợi Ý Chính
Sử dụng hàm `rotate_image()` với tham số `angle`.

**Các góc xoay phổ biến:**
- `90` = Xoay 90 độ theo chiều kim đồng hồ
- `180` = Xoay 180 độ (lộn ngược)
- `270` = Xoay 270 độ (hoặc -90 độ)

## Cấu Trúc Code
```python
# 1. Khởi tạo camera
# 2. Trong vòng lặp:
#    - Lấy khung hình
#    - Xoay ảnh: rotated_frame = rotate_image(camera_frame=..., angle=90)
#    - Hiển thị ảnh đã xoay
# 3. Đóng camera
```

## Hàm Cần Dùng:
- `rotate_image(camera_frame=..., angle=...)` - Xoay ảnh
