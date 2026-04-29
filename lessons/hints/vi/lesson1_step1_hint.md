# 💡 Gợi Ý - Hint: My First Camera

## Bước 1: Khởi tạo Camera
Bạn cần sử dụng hàm `Init_Camera()` để khởi động camera. Hàm này trả về một đối tượng camera mà bạn cần lưu vào biến.

**Gợi ý:**
```python
capture_camera = Init_Camera()
```

## Bước 2: Lấy Khung Hình
Trong vòng lặp `while True`, sử dụng hàm `Get_Camera_Frame()` để lấy từng khung hình từ camera.

**Gợi ý:**
- Truyền tham số `capture_camera` vào hàm
- Lưu kết quả vào biến `camera_frame`

## Bước 3: Hiển Thị Hình Ảnh
Sử dụng hàm `Show_Image()` để hiển thị khung hình lên màn hình.

**Gợi ý:**
- Truyền tham số `camera_frame` vào hàm

## Bước 4: Đóng Camera
Sau vòng lặp, sử dụng hàm `Close_Camera()` để đóng camera đúng cách.

**Gợi ý:**
- Truyền tham số `capture_camera` vào hàm

## Các Hàm Cần Dùng:
- `Init_Camera()` - Khởi tạo camera
- `Get_Camera_Frame(capture_camera=...)` - Lấy khung hình
- `Show_Image(camera_frame=...)` - Hiển thị hình
- `Close_Camera(capture_camera=...)` - Đóng camera
