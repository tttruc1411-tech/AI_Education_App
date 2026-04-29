# 💡 Gợi Ý - Hint: Draw Circle

## Mục Tiêu
Vẽ hình tròn lên ảnh.

## Gợi Ý Chính
Sử dụng hàm `Draw_Circle()` với tâm và bán kính.

**Tham số:**
- `center_x, center_y` = Tọa độ tâm hình tròn
- `radius` = Bán kính
- `color` = Màu sắc (green, red, blue, yellow, white)

**Ví dụ:**
```python
Draw_Circle(camera_frame=frame, center_x=320, center_y=240, radius=50, color=red)
```

## Cấu Trúc Code
```python
# 1. Khởi tạo camera
# 2. Trong vòng lặp:
#    - Lấy khung hình
#    - Vẽ hình tròn
#    - Hiển thị ảnh
# 3. Đóng camera
```

## Hàm Cần Dùng:
- `Draw_Circle(camera_frame=..., center_x=..., center_y=..., radius=..., color=...)` - Vẽ hình tròn
