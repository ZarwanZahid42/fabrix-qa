"""
Patch Extractor — Preprocessing Pipeline
==========================================
Splits high-resolution fabric images into fixed-size patches for model training.

Features:
  - Configurable patch size (default: 256×256 px)
  - Stride control to generate overlapping patches
  - Preserves label annotations (YOLO format)
  - Outputs train/val/test split (default: 70/15/15)

Usage:
  python preprocessing/patch_extractor.py \
    --source datasets/raw/aitex \
    --output datasets/processed \
    --patch-size 256 \
    --stride 128

TODO: Implement PatchExtractor class
"""

import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Extract image patches for training")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--patch-size", type=int, default=256)
    parser.add_argument("--stride", type=int, default=128)
    parser.add_argument("--split", nargs=3, type=float, default=[0.7, 0.15, 0.15])
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raise NotImplementedError("Implement PatchExtractor in Phase 2")
