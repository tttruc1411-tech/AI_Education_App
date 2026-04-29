# ============================================================
# LESSON 1: Camera Basics - CHALLENGE
# TITLE: Smart Photo Booth
# TITLE_VI: Gian Hàng Chụp Ảnh Thông Minh
# ============================================================

# Import camera, image processing, and display modules
import camera
import image
import display

# TODO: Write complete code here
# Initialize the camera


# Frame counter variable
frame_count = 0

print("[OK] Photo Booth ready! Smile in 3 seconds...")

# Main loop
while True:
    # Get a frame
    
    
    # Flip the image horizontally
    
    
    # Display
    
    
    # Count frames
    frame_count += 1
    
    # After 90 frames (about 3 seconds), take a photo
    if frame_count == 90:
        # TODO: Save the image
        
        print("[OK] Photo captured!")
        frame_count = 0  # Reset counter

# Close the camera


