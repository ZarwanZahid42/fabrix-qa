"""
Augmentation Pipeline — Albumentations
========================================
Defines the training-time augmentation pipeline for fabric defect images.

Augmentations applied:
  - RandomRotate90, HorizontalFlip, VerticalFlip
  - RandomBrightnessContrast
  - GaussNoise, MotionBlur (simulate camera noise)
  - GridDistortion (simulate fabric stretch)
  - CLAHE (enhance contrast for low-visibility defects)

TODO: Tune augmentation probabilities after baseline evaluation
"""

import albumentations as A
from albumentations.pytorch import ToTensorV2

TRAIN_TRANSFORMS = A.Compose([
    A.RandomRotate90(p=0.5),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.3),
    A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
    A.GaussNoise(var_limit=(10, 50), p=0.3),
    A.MotionBlur(blur_limit=3, p=0.2),
    A.GridDistortion(p=0.2),
    A.CLAHE(clip_limit=2.0, p=0.3),
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2(),
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

VAL_TRANSFORMS = A.Compose([
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2(),
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))
