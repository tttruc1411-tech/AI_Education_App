# 💡 Gợi Ý - Hint: Edge Detection

## Mục Tiêu
Phát hiện cạnh trong ảnh (edge detection).

## Gợi Ý Chính
Sử dụng hàm `detect_edges()` để tìm các cạnh.

**Lưu ý:**
- Kết quả sẽ là ảnh đen trắng với các cạnh được highlight
- Hoạt động tốt nhất với ảnh có độ tương phản cao

## Cấu Trúc Code
```python
# 1. Khởi tạo camera
# 2. Trong vòng lặp:
#    - Lấy khung hình
#    - Phát hiện cạnh: edges_frame = detect_edges(camera_frame=...)
#    - Hiển thị ảnh cạnh
# 3. Đóng camera
```

## Hàm Cần Dùng:
- `detect_edges(camera_frame=...)` - Phát hiện cạnh
