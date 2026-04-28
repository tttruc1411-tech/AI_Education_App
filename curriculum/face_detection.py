# TITLE: Face Detection (YuNet)
# TITLE_VI: Nhận diện khuôn mặt (YuNet)
# LEVEL: Intermediate
# ICON: 👤
# COLOR: #eab308
# DESC: Detect faces in real-time camera feed using the YuNet ONNX model.
# DESC_VI: Nhận diện khuôn mặt trong thời gian thực bằng mô hình YuNet ONNX.
# ORDER: 1
# ============================================================


import ai_vision
import camera
import drawing

# 1. Setup specialized AI Face Model
detector = ai_vision.Load_YuNet_Model('projects/model/face_detection_yunet_2023mar.onnx')

# 2. Initialize Camera
cap = camera.Init_Camera()
print("[OK] Starting AI Face Detection...")

while True:
    # Read frame from camera
    frame = camera.Get_Camera_Frame(cap)        
    # 3. Prepare AI Inference
    ai_vision.Run_YuNet_Model(detector, frame)    
    # 4. Run AI Model
    _, faces = detector.detect(frame)
    
    # 5. Draw Boxes & Labels (Returns face count)
    face_count = drawing.Draw_Detections(frame, faces, label="Face")
    
    # 6. Stream Live Feed to App & Track Count
    drawing.Update_Dashboard(frame, var_name="Faces Found", var_value=face_count)

cap.release()
print("[OK] Session Ended.")