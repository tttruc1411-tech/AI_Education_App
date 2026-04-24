# src/modules/library/functions/drawing_blocks.py
#
# Drawing and dashboard functions for AI detection results.
# Usage: import drawing
# Then:  drawing.Draw_Detections(), drawing.Update_Dashboard(), etc.

import sys
import base64
import cv2
import numpy as np


def Draw_Detections(camera_frame, results, label="Detected"):
    """
    Draws bounding boxes and labels for AI detection results.
    - Face Mode (YuNet): Results as [x, y, w, h, ...] (15 values total)
    - Object Mode (YOLOv10): Results as [x1, y1, x2, y2, confidence, class_id]
    - Simple Mode: [x, y, w, h]
    """
    count = 0
    if results is not None:
        count = len(results)
        for f in results:
            # Different models have different output columns!

            # --- INTERMEDIATE MODE: YOLOv10 (Length 6) ---
            if len(f) == 6:
                x1, y1, x2, y2, conf, cls = f[0], f[1], f[2], f[3], f[4], f[5]
                x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)

                name = label[int(cls)] if isinstance(label, list) else f"{label} {int(cls)}"
                display_text = f"{name} ({conf*100:.0f}%)"

            # --- BEGINNER MODE: Face Detection (YuNet has 15 columns) ---
            elif len(f) == 15:
                x, y, w, h = map(int, f[0:4])
                conf = f[14]
                display_text = f"{label} ({conf*100:.0f}%)" if label else f"Face ({conf*100:.0f}%)"

            # --- BASIC MODE: Simple Boxes (Length 4) ---
            else:
                x, y, w, h = map(int, f[:4])
                display_text = label

            # 1. Draw Bounding Box
            cv2.rectangle(camera_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # 2. Draw Label Background
            (tw, th), _ = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            cv2.rectangle(camera_frame, (x, y - th - 10), (x + tw, y), (0, 255, 0), -1)

            # 3. Draw Text (Solid Black for maximum contrast)
            cv2.putText(camera_frame, display_text, (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    return count


def Update_Dashboard(camera_frame, var_name=None, var_value=None):
    """
    Sends the frame to the Live Feed and optionally updates a variable in the Results panel.
    """
    # 1. Update Variable if provided
    if var_name is not None:
        print(f"VAR:{var_name}:{var_value}")

    # 2. Stream Frame to UI
    if camera_frame is not None:
        ok, buffer = cv2.imencode('.jpg', camera_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if ok:
            img_b64 = base64.b64encode(buffer).decode('utf-8')
            print(f"IMG:{img_b64}")

    # 3. Flush output for real-time performance
    sys.stdout.flush()


def Draw_Detections_MultiClass(camera_frame, outputs, classes, conf_threshold=0.50):
    """
    Advanced block that parses raw YOLO ONNX output, scales coordinates,
    applies Non-Maximum Suppression (NMS), and draws the results!
    Supports both YOLOv10 [1, 300, 6] and YOLOv8/v11 [1, N_classes+4, N_anchors] formats.
    """
    if len(outputs) == 0: return 0
    conf_threshold = float(conf_threshold)

    fh, fw, _ = camera_frame.shape
    raw = outputs[0]  # shape: [1, 300, 6] or [1, C+4, N]

    boxes, confidences, class_ids = [], [], []

    # Detect output format by shape
    if raw.ndim == 3 and raw.shape[1] < raw.shape[2]:
        # YOLOv8/v11 transposed format: [1, 4+num_classes, num_anchors]
        data = raw[0].T
        num_classes = data.shape[1] - 4

        # Determine model input size from anchor count
        n_anchors = raw.shape[2]
        img_size = 320 if n_anchors <= 4200 else 640
        sx, sy = fw / img_size, fh / img_size

        for row in data:
            scores = row[4:]
            cid = int(np.argmax(scores))
            cf = float(scores[cid])
            if cf < conf_threshold:
                continue
            cx, cy, w, h = row[:4]
            x1 = int((cx - w / 2) * sx)
            y1 = int((cy - h / 2) * sy)
            boxes.append([x1, y1, int(w * sx), int(h * sy)])
            confidences.append(cf)
            class_ids.append(cid)
    else:
        # YOLOv10 format: [1, 300, 6]
        detections = raw[0]

        for i in range(len(detections)):
            det = detections[i]

            # DYNAMIC COLUMN FIX
            if det[4] > 1.0 or det[4].is_integer():
                class_id = int(det[4])
                confidence = float(det[5])
            else:
                confidence = float(det[4])
                class_id = int(det[5])

            if confidence > conf_threshold:
                if det[2] <= 1.5:
                    x1 = int(det[0] * fw)
                    y1 = int(det[1] * fh)
                    x2 = int(det[2] * fw)
                    y2 = int(det[3] * fh)
                else:
                    x1 = int(det[0] * (fw / 640))
                    y1 = int(det[1] * (fh / 640))
                    x2 = int(det[2] * (fw / 640))
                    y2 = int(det[3] * (fh / 640))

                width = x2 - x1
                height = y2 - y1

                boxes.append([x1, y1, width, height])
                confidences.append(confidence)
                class_ids.append(class_id)

    # Filtering overlapping boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, 0.4)

    count = 0
    if len(indices) > 0:
        for i in indices:
            idx = int(i) if isinstance(i, (int, np.integer)) else i[0]

            x, y, width, height = boxes[idx]
            conf = confidences[idx]
            cls_id = class_ids[idx]
            x2, y2 = x + width, y + height

            name = classes[cls_id] if cls_id < len(classes) else f"ID:{cls_id}"
            display_text = f"{name} ({conf*100:.0f}%)"

            cv2.rectangle(camera_frame, (x, y), (x2, y2), (0, 255, 0), 2)

            (tw, th), _ = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            cv2.rectangle(camera_frame, (x, y - th - 10), (x + tw, y), (0, 255, 0), -1)

            cv2.putText(camera_frame, display_text, (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)

            count += 1

    return count


def Draw_Engine_Detections(camera_frame, results, classes=None, conf_threshold=0.25):
    """
    High-fidelity drawing block for .engine model results.
    Filters detections below conf_threshold before drawing.
    Returns the number of objects detected.
    """
    if results:
        conf_threshold = float(conf_threshold)
        results = [r for r in results if len(r) >= 5 and r[4] >= conf_threshold]
    return Draw_Detections(camera_frame, results, label=classes if classes else "Object")
