"""
Train YOLOv8n trên Jetson Orin Nano Super (8GB shared RAM)
Sau khi train xong, tự động convert sang TensorRT Engine

Tối ưu cho Jetson:
  - batch=2 (an toàn khi app chạy song song)
  - freeze=5 (giữ low-level features, chống overfit với dataset nhỏ)
  - cache=True (load ảnh vào RAM, giảm I/O)
  - Giới hạn: max 200 ảnh (640x640) hoặc 500 ảnh (320x320)

Usage:
  python3 train.py --model models/yolov8n.pt --data data/datasets/my_data/dataset.yaml
  python3 train.py --model models/yolov8n.pt --data data/datasets/my_data/dataset.yaml --epochs 30
  python3 train.py --model models/yolov8n.pt --data data/datasets/my_data/dataset.yaml --no-convert

Chuẩn bị dataset:
  Tạo file dataset.yaml:
    path: /absolute/path/to/dataset
    train: images/train
    val: images/val
    names:
      0: class_a
      1: class_b

  Cấu trúc thư mục:
    data/datasets/my_dataset/
    ├── images/
    │   ├── train/    # ảnh train (.jpg, .png) — 80%
    │   └── val/      # ảnh validation — 20%
    └── labels/
        ├── train/    # label YOLO format (.txt)
        └── val/
"""
import argparse
import os
import sys
import time

# ======================== THÔNG SỐ TỐI ƯU CHO JETSON ========================
TRAIN_CONFIG = {
    "batch": 2,          # Cố định - an toàn cho 8GB shared RAM + app chạy song song
    "workers": 2,        # 2/6 CPU cores cho data loading
    "freeze": 5,         # Đóng băng layer 0-4 (universal features)
                         # Layer 5+ train lại cho domain mới
    "cache": True,       # Load ảnh vào RAM trước → giảm ~15-20% thời gian
    "patience": 20,      # Early stopping nếu không cải thiện sau 20 epochs
    "plots": False,      # Tắt vẽ biểu đồ → tiết kiệm I/O
    "exist_ok": True,
    "save": True,
    "device": 0,
}
# =============================================================================


def train(model_name, data_yaml, epochs, imgsz, no_convert):
    from ultralytics import YOLO

    if not os.path.exists(data_yaml):
        print(f"ERROR: Không tìm thấy {data_yaml}")
        print("Tạo file dataset.yaml trước. Xem hướng dẫn: python3 train.py --help")
        sys.exit(1)

    print("=" * 60)
    print(f" TRAIN: {model_name}")
    print(f" Dataset: {data_yaml}")
    print(f" Epochs: {epochs} | Batch: {TRAIN_CONFIG['batch']} | ImgSz: {imgsz}")
    print(f" Freeze: {TRAIN_CONFIG['freeze']} layers | Cache: {TRAIN_CONFIG['cache']}")
    print("=" * 60)

    model = YOLO(model_name)

    t0 = time.time()
    model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        **TRAIN_CONFIG,
    )
    train_time = time.time() - t0
    print(f"\nTrain xong: {train_time:.0f}s ({train_time/60:.1f} phút)")

    # Tìm best.pt
    best_pt = os.path.join(model.trainer.save_dir, "weights", "best.pt")
    if not os.path.exists(best_pt):
        print(f"WARNING: Không tìm thấy {best_pt}")
        return

    print(f"Best model: {best_pt}")

    # Auto convert sang engine
    if not no_convert:
        print("\n--- Auto convert sang TensorRT Engine ---")
        from convert import convert
        convert(best_pt)
    else:
        print(f"\nĐể convert thủ công: python3 convert.py {best_pt}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv8n trên Jetson Orin Nano Super")
    parser.add_argument("--model", type=str, default="models/yolov8n.pt",
                        help="Model pretrained (default: models/yolov8n.pt)")
    parser.add_argument("--data", type=str, required=True,
                        help="Path đến dataset.yaml")
    parser.add_argument("--epochs", type=int, default=20,
                        help="Số epochs (default: 20)")
    parser.add_argument("--imgsz", type=int, default=640,
                        help="Input size (default: 640)")
    parser.add_argument("--no-convert", action="store_true",
                        help="Không tự động convert sau khi train")

    args = parser.parse_args()
    train(args.model, args.data, args.epochs, args.imgsz, args.no_convert)
