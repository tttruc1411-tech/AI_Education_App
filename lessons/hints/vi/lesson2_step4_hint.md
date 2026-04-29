# 💡 Gợi Ý - Hint: Resize Image

## Mục Tiêu
Thay đổi kích thước ảnh.

## Gợi Ý Chính
Sử dụng hàm `resize_image()` với tham số `width` và `height`.

**Ví dụ kích thước:**
- `width=320, height=240` = Nhỏ
- `width=640, height=480` = Trung bình
- `width=1280, height=720` = Lớn (HD)

## Cấu Trúc Code
```python
# 1. Khởi tạo camera
# 2. Trong vòng lặp:
#    - Lấy khung hình
#    - Resize: resized_frame = resize_image(camera_frame=..., width=320, height=240)
#    - Hiển thị ảnh đã resize
# 3. Đóng camera
```

## Hàm Cần Dùng:
- `resize_image(camera_frame=..., width=..., height=...)` - Thay đổi kích thước
