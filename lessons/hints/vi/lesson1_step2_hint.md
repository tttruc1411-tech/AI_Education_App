# 💡 Gợi Ý - Hint: Save & Load Pictures

## Bước 1: Khởi Tạo và Chụp Ảnh
Khởi tạo camera và lấy một khung hình để chụp.

**Gợi ý:**
```python
capture_camera = Init_Camera()
camera_frame = Get_Camera_Frame(capture_camera=capture_camera)
```

## Bước 2: Lưu Ảnh
Sử dụng hàm `Save_Frame()` để lưu khung hình vào file.

**Gợi ý:**
- Tham số 1: `camera_frame` - khung hình cần lưu
- Tham số 2: `file_path` - tên file (ví dụ: 'my_photo.jpg')

## Bước 3: Đóng Camera
Đóng camera sau khi chụp xong.

## Bước 4: Tải Ảnh Đã Lưu
Sử dụng hàm `Load_Image()` để tải ảnh từ file.

**Gợi ý:**
```python
loaded_image = Load_Image(file_path='my_photo.jpg')
```

## Bước 5: Hiển Thị Ảnh
Hiển thị ảnh đã tải lên màn hình.

## Các Hàm Cần Dùng:
- `Save_Frame(camera_frame=..., file_path=...)` - Lưu ảnh
- `Load_Image(file_path=...)` - Tải ảnh
