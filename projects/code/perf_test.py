# TITLE: Model Comparison
# TITLE_VI: So sánh mô hình
# LEVEL: Advanced
# ICON: ⚡
# COLOR: #f59e0b
# DESC: Compare V8 vs V11 detection live. Press Shift+Space to toggle model.
# DESC_VI: So sánh nhận diện V8 và V11 trực tiếp. Nhấn Shift+Space để chuyển mô hình.
# ============================================================

import os, sys, select, time, base64
sys.stdout.reconfigure(line_buffering=True)
os.environ["OPENCV_LOG_LEVEL"] = "SILENT"
os.environ["ORT_LOG_LEVEL"] = "ERROR"

import cv2
import numpy as np
import onnxruntime as ort
ort.set_default_logger_severity(3)

CLASSES = ["servo", "socket"]
IMG_SIZE = 320
CONF = 0.50

# ── Provider selection (prefer GPU) ──
available = ort.get_available_providers()
providers = []
if 'CUDAExecutionProvider' in available:
    providers.append(('CUDAExecutionProvider', {'device_id': 0}))
providers.append('CPUExecutionProvider')
gpu_tag = "GPU" if 'CUDAExecutionProvider' in available else "CPU"
print(f"[ONNX] Providers: {[p if isinstance(p,str) else p[0] for p in providers]}")

# ── Load both models ──
print("Loading V8...")
s_v8 = ort.InferenceSession('projects/model/V8.onnx', providers=providers)
print("Loading V11...")
s_v11 = ort.InferenceSession('projects/model/V11.onnx', providers=providers)
print(f"[ONNX] Active: {s_v8.get_providers()}")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERROR: Cannot open camera")
    sys.exit(1)

sessions = [s_v8, s_v11]
names = ["V8", "V11"]
cur = 0
fc, t0 = 0, time.perf_counter()

print(f"[OK] Active: {names[cur]} {gpu_tag} | Shift+Space to switch")

while True:
    # Check for toggle
    if select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline().strip()
        if line == "CMD:TOGGLE":
            cur = (cur + 1) % 2
            fc, t0 = 0, time.perf_counter()
            print(f"[SWITCH] {names[cur]}")

    ret, frame = cap.read()
    if not ret:
        continue

    fh, fw = frame.shape[:2]
    sx, sy = fw / IMG_SIZE, fh / IMG_SIZE

    # Inference
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (IMG_SIZE, IMG_SIZE), swapRB=True, crop=False)
    inp_name = sessions[cur].get_inputs()[0].name
    raw = sessions[cur].run(None, {inp_name: blob})[0]

    # Parse [1, 6, 2100] → [2100, 6] YOLOv8 format
    data = raw[0].T
    boxes, confs, cls_ids = [], [], []
    for row in data:
        scores = row[4:]
        cid = int(np.argmax(scores))
        cf = float(scores[cid])
        if cf < CONF:
            continue
        cx, cy, w, h = row[:4]
        x1 = int((cx - w/2) * sx)
        y1 = int((cy - h/2) * sy)
        boxes.append([x1, y1, int(w * sx), int(h * sy)])
        confs.append(cf)
        cls_ids.append(cid)

    # NMS + Draw
    count = 0
    indices = cv2.dnn.NMSBoxes(boxes, confs, CONF, 0.4)
    if len(indices) > 0:
        for i in indices:
            idx = int(i) if isinstance(i, (int, np.integer)) else i[0]
            bx, by, bw, bh = boxes[idx]
            name = CLASSES[cls_ids[idx]] if cls_ids[idx] < len(CLASSES) else f"ID:{cls_ids[idx]}"
            label = f"{name} ({confs[idx]*100:.0f}%)"
            cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), (0, 255, 0), 2)
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (bx, by-th-10), (bx+tw, by), (0, 255, 0), -1)
            cv2.putText(frame, label, (bx, by-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
            count += 1

    # FPS
    fc += 1
    fps = fc / (time.perf_counter() - t0)

    # OSD
    info = f"{names[cur]} {gpu_tag} | {fps:.1f} FPS | {count} obj"
    cv2.putText(frame, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 3)
    cv2.putText(frame, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

    # Stream to app
    ok, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
    if ok:
        print(f"IMG:{base64.b64encode(buf).decode('utf-8')}")
