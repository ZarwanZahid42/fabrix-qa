"""
YOLOv8 Training Script
=======================
Trains a YOLOv8 model on the processed FabriX dataset for fabric defect detection.

Usage:
  python training/train_yolo.py --data datasets/processed/data.yaml \
                                 --model yolov8n.pt \
                                 --epochs 100 \
                                 --imgsz 640

TODO:
  - Add MLflow experiment tracking integration
  - Add early stopping callback
  - Log confusion matrix and mAP curves as artifacts
"""

import argparse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Train YOLOv8 for fabric defect detection")
    parser.add_argument("--data", type=str, required=True, help="Path to data.yaml")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="Base model weights")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device", type=str, default="0", help="GPU device (0) or cpu")
    parser.add_argument("--project", type=str, default="runs/detect")
    parser.add_argument("--name", type=str, default="fabrix_yolo")
    return parser.parse_args()


def main():
    args = parse_args()
    # TODO: Initialize MLflow run
    # TODO: Load Ultralytics YOLO model and call model.train(...)
    print(f"[FabriX-QA] Training YOLOv8 on {args.data} for {args.epochs} epochs")
    raise NotImplementedError("Implement in Phase 2")


if __name__ == "__main__":
    main()
