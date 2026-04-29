# ============================================================
# LESSON 1: Camera Basics - CHALLENGE
# TITLE: Smart Photo Booth
# TITLE_VI: Gian Hàng Chụp Ảnh Thông Minh
# ============================================================

# Import camera, image processing, và display modules
import camera
import image
import display

# TODO: Viết code hoàn chỉnh ở đây
# Khởi tạo camera


# Biến đếm khung hình
frame_count = 0

print("[OK] Photo Booth ready! Smile in 3 seconds...")

# Vòng lặp chính
while True:
    # Lấy khung hình
    
    
    # Lật ảnh theo chiều ngang
    
    
    # Hiển thị
    
    
    # Đếm khung hình
    frame_count += 1
    
    # Sau 90 khung hình (khoảng 3 giây), chụp ảnh
    if frame_count == 90:
        # TODO: Lưu ảnh
        
        print("[OK] Photo captured!")
        frame_count = 0  # Reset đếm

# Đóng camera

