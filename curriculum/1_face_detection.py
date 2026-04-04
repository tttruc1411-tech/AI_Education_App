# TITLE: Face Detection (YuNet)
# TITLE_VI: Nhận diện khuôn mặt (YuNet)
# LEVEL: Beginner
# ICON: 👤
# COLOR: #7c3aed
# DESC: Detect faces in real-time camera feed using the YuNet ONNX model.
# DESC_VI: Nhận diện khuôn mặt trong thời gian thực bằng mô hình YuNet ONNX.
# ============================================================

import cv2
from src.modules.library.functions.ai_blocks import (
    Init_Camera, Get_Camera_Frame, Load_YuNet_Model, Run_YuNet_Model, Draw_Detections, Update_Dashboard
)

# 1. Setup specialized AI Face Model
detector = Load_YuNet_Model('projects/model/face_detection_yunet_2023mar.onnx')

# 2. Initialize Camera
cap = Init_Camera()
print("[OK] Starting AI Face Detection...")

while True:
    # Read frame from camera
    frame = Get_Camera_Frame(cap)        
    # 3. Prepare AI Inference
    Run_YuNet_Model(detector, frame)    
    # 4. Run AI Model
    _, faces = detector.detect(frame)
    
    # 5. Draw Boxes & Labels (Returns face count)
    face_count = Draw_Detections(frame, faces, label="Face")
    
    # 6. Stream Live Feed to App & Track Count
    Update_Dashboard(frame, var_name="Faces Found", var_value=face_count)

cap.release()
print("[OK] Session Ended.")