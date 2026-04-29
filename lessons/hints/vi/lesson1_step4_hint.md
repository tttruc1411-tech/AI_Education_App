# 💡 Gợi Ý - Hint: Brightness Control

## Mục Tiêu
Điều chỉnh độ sáng của ảnh.

## Gợi Ý Chính
Sử dụng hàm `adjust_brightness()` với tham số `brightness_value`.

**Giá trị brightness:**
- `< 0` = Tối hơn (darker)
- `0` = Không đổi
- `> 0` = Sáng hơn (brighter)
- Ví dụ: `50` = Tăng độ sáng 50 đơn vị

## Cấu Trúc Code
```python
# 1. Khởi tạo camera
# 2. Trong vòng lặp:
#    - Lấy khung hình
#    - Điều chỉnh độ sáng: bright_frame = adjust_brightness(camera_frame=..., brightness_value=50)
#    - Hiển thị ảnh đã điều chỉnh
# 3. Đóng camera
```

## Hàm Cần Dùng:
- `adjust_brightness(camera_frame=..., brightness_value=...)` - Điều chỉnh độ sáng
