# 💡 Gợi Ý - Hint: Mirror Selfie Mode

## Mục Tiêu
Tạo hiệu ứng gương (mirror) bằng cách lật ảnh theo chiều ngang.

## Gợi Ý Chính
Sử dụng hàm `flip_image()` với tham số `flip_code=1` để lật ảnh theo chiều ngang.

**Các giá trị flip_code:**
- `0` = Lật theo chiều dọc (vertical)
- `1` = Lật theo chiều ngang (horizontal) ← Dùng cái này!
- `-1` = Lật cả 2 chiều

## Cấu Trúc Code
```python
# 1. Khởi tạo camera
# 2. Trong vòng lặp:
#    - Lấy khung hình
#    - Lật ảnh: flipped_frame = flip_image(camera_frame=..., flip_code=1)
#    - Hiển thị ảnh đã lật
# 3. Đóng camera
```

## Hàm Cần Dùng:
- `flip_image(camera_frame=..., flip_code=1)` - Lật ảnh
