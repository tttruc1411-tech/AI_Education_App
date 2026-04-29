# Lesson 3 - Challenge: Creative Art Canvas
## Thách thức / Challenge
Tạo một tác phẩm nghệ thuật bằng các hình dạng.

## Yêu cầu / Requirements
Tạo một bức tranh "ngôi nhà" đơn giản bằng cách vẽ:
1. Khởi tạo camera
2. Vẽ một "ngôi nhà" gồm:
   - Thân nhà: Hình chữ nhật màu xanh dương (x=200, y=250, width=240, height=200)
   - Mái nhà: Hình chữ nhật màu đỏ (x=180, y=200, width=280, height=60)
   - Cửa sổ trái: Hình chữ nhật màu vàng (x=230, y=300, width=60, height=60)
   - Cửa sổ phải: Hình chữ nhật màu vàng (x=350, y=300, width=60, height=60)
   - Cửa ra vào: Hình chữ nhật màu trắng (x=280, y=370, width=80, height=80)
3. Vẽ "mặt trời": Hình tròn màu vàng (center_x=550, center_y=100, radius=50)
4. Hiển thị tác phẩm
5. Đóng camera khi kết thúc

## Functions cần dùng
- `Init_Camera()`, `Get_Camera_Frame()`, `Close_Camera()`
- `Draw_Rectangle(camera_frame, x, y, width, height, color)`
- `Draw_Circle(camera_frame, center_x, center_y, radius, color)`
- `Show_Image(camera_frame)`

## Mục tiêu học tập
Kết hợp nhiều hình dạng và màu sắc để tạo ra một tác phẩm nghệ thuật hoàn chỉnh.

## Gợi ý
- Vẽ theo thứ tự từ dưới lên trên (thân nhà → mái → cửa sổ → cửa)
- Có thể thêm các chi tiết khác để trang trí (cỏ, mây, ...)
