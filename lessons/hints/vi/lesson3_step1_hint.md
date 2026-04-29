# 💡 Gợi Ý - Hint: Draw Rectangle

## Mục Tiêu
Vẽ hình chữ nhật lên ảnh.

## Gợi Ý Chính
Sử dụng hàm `Draw_Rectangle()` với các tham số vị trí và kích thước.

**Tham số:**
- `x, y` = Tọa độ góc trên bên trái
- `width, height` = Chiều rộng và chiều cao
- `color` = Màu sắc (green, red, blue, yellow, white)

**Ví dụ:**
```python
Draw_Rectangle(camera_frame=frame, x=100, y=100, width=200, height=150, color=green)
```

## Cấu Trúc Code
```python
# 1. Khởi tạo camera
# 2. Trong vòng lặp:
#    - Lấy khung hình
#    - Vẽ hình chữ nhật
#    - Hiển thị ảnh
# 3. Đóng camera
```

## Hàm Cần Dùng:
- `Draw_Rectangle(camera_frame=..., x=..., y=..., width=..., height=..., color=...)` - Vẽ hình chữ nhật
