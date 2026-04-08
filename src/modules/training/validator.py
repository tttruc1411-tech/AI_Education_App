"""
Fast Validation: Live camera detection using a trained YOLO model.
Launched as a QProcess by main.py — streams annotated frames via IMG: protocol.
"""
import sys
import os
import argparse
import base64
import cv2
import numpy as np

# Colors matching the MultiClassTagPanel palette (BGR for OpenCV)
PALETTE = [
    (0xf7, 0x55, 0xa8),  # Purple  #a855f7
    (0x85, 0x71, 0xfb),  # Rose    #fb7185
    (0xf6, 0x82, 0x3b),  # Blue    #3b82f6
    (0x81, 0xb9, 0x10),  # Emerald #10b981
]


def draw_detections(frame, detections, class_names):
    """Draw bounding boxes and labels on frame. detections: list of [x1,y1,x2,y2,conf,cls]"""
    for det in detections:
        if len(det) < 6:
            continue
        x1, y1, x2, y2, conf, cls_id = det[:6]
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        cls_id = int(cls_id)
        color = PALETTE[cls_id % len(PALETTE)]

        name = class_names[cls_id] if cls_id < len(class_names) else f"Class {cls_id}"
        label = f"{name} {conf * 100:.0f}%"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
        cv2.putText(frame, label, (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Path to .engine or .pt model")
    parser.add_argument("--names", required=True, help="Comma-separated class names")
    parser.add_argument("--imgsz", type=int, default=640)
    args = parser.parse_args()

    class_names = [n.strip() for n in args.names.split(",")]

    # Load model
    try:
        import torch
        torch.cuda.empty_cache()
        from ultralytics import YOLO
        model = YOLO(args.model, task="detect")
        print("STATUS: Model loaded for validation.", flush=True)
    except Exception as e:
        print(f"ERROR: Failed to load model: {e}", flush=True)
        sys.exit(1)

    # Open camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Cannot open camera.", flush=True)
        sys.exit(1)

    print("STATUS: Validation stream started.", flush=True)

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue

            # Run inference
            results = model(frame, imgsz=args.imgsz, verbose=False)
            detections = []
            if len(results) > 0 and len(results[0].boxes) > 0:
                detections = results[0].boxes.data.tolist()

            # Draw detections
            draw_detections(frame, detections, class_names)

            # Encode and stream
            ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ok:
                b64 = base64.b64encode(buf).decode("utf-8")
                print(f"IMG:{b64}", flush=True)

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        try:
            import torch
            torch.cuda.empty_cache()
        except Exception:
            pass
        print("STATUS: Validation stopped.", flush=True)


if __name__ == "__main__":
    main()
