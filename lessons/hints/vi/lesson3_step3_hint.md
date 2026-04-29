# 💡 Gợi Ý - Hint: Multiple Shapes

## Mục Tiêu
Vẽ nhiều hình dạng khác nhau trên cùng một ảnh.

## Gợi Ý Chính
Gọi nhiều hàm vẽ lần lượt trên cùng một khung hình.

**Ví dụ:**
```python
# Vẽ hình chữ nhật
Draw_Rectangle(camera_frame=frame, x=50, y=50, width=100, height=80, color=green)

# Vẽ hình tròn
Draw_Circle(camera_frame=frame, center_x=200, center_y=200, radius=40, color=red)

# Vẽ thêm hình chữ nhật khác
Draw_Rectangle(camera_frame=frame, x=300, y=100, width=120, height=90, color=blue)
```

## Cấu Trúc Code
```python
# 1. Khởi tạo camera
# 2. Trong vòng lặp:
#    - Lấy khung hình
#    - Vẽ hình 1
#    - Vẽ hình 2
#    - Vẽ hình 3
#    - Hiển thị ảnh
# 3. Đóng camera
```

## Lưu Ý:
- Tất cả các hình vẽ trên cùng một `camera_frame`
- Hình vẽ sau sẽ đè lên hình vẽ trước nếu trùng vị trí
