# TITLE: Object Detection
# TITLE_VI: Nhận diện vật thể (YOLOv10)
# LEVEL: Intermediate
# ICON: 🔍
# COLOR: #22c55e
# DESC: Detect 80+ objects with YOLOv10.
# DESC_VI: Nhận diện hơn 80 loại vật thể khác nhau bằng mô hình YOLOv10.
# ============================================================

import cv2
from src.modules.library.functions.ai_blocks import Init_Camera, Update_Dashboard, Draw_Detections_MultiClass, Load_ONNX_Model, Run_ONNX_Model, Get_Camera_Frame
my code
# 1. Full COCO Labels
CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
    "chair", "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop",
    "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]

# 2. Load the AI Model
model_path = "projects/model/yolov10n.onnx"
session = Load_ONNX_Model(model_path)
if session is None: exit()

cap = Init_Camera(0)
print("[OK] Starting Real-time Object Detection!")

while True:
    frame = Get_Camera_Frame(cap)    
        
    # 3. Process the Image directly through the Brain
    outputs = Run_ONNX_Model(session, frame, img_size=640)
    
    # 4. Draw AI Detections (Multi-Class)
    count = Draw_Detections_MultiClass(frame, outputs, CLASSES, 0.50)

    # 6. Send frame to Dashboard API
    Update_Dashboard(frame, var_name="Detections", var_value=count)
