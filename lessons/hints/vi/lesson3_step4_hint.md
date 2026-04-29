# 💡 Gợi Ý - Hint: Color Variations

## Mục Tiêu
Vẽ nhiều hình với màu sắc khác nhau.

## Gợi Ý Chính
Sử dụng các màu khác nhau cho mỗi hình vẽ.

**Màu sắc có sẵn:**
- `green` = Xanh lá
- `red` = Đỏ
- `blue` = Xanh dương
- `yellow` = Vàng
- `white` = Trắng

**Ví dụ:**
```python
# Hình chữ nhật xanh lá
Draw_Rectangle(camera_frame=frame, x=50, y=50, width=100, height=80, color=green)

# Hình tròn đỏ
Draw_Circle(camera_frame=frame, center_x=200, center_y=150, radius=40, color=red)

# Hình chữ nhật xanh dương
Draw_Rectangle(camera_frame=frame, x=300, y=200, width=80, height=100, color=blue)

# Hình tròn vàng
Draw_Circle(camera_frame=frame, center_x=400, center_y=300, radius=50, color=yellow)
```

## Cấu Trúc Code
```python
# 1. Khởi tạo camera
# 2. Trong vòng lặp:
#    - Lấy khung hình
#    - Vẽ nhiều hình với màu khác nhau
#    - Hiển thị ảnh
# 3. Đóng camera
```

## Thử Nghiệm:
- Thử vẽ ít nhất 4 hình với 4 màu khác nhau
- Sắp xếp vị trí sao cho đẹp mắt
