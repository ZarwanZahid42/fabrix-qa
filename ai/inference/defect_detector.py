"""
Defect Detector — Inference Module
====================================
Loads trained YOLOv8 weights and runs real-time defect detection on incoming frames.

Interface:
  detector = DefectDetector(model_path="models/fabrix_yolo_best.pt")
  results = detector.predict(frame)  # frame: np.ndarray (BGR)
  # results: List[DefectDetection(bbox, class_name, confidence, severity)]

TODO:
  - Implement DefectDetector class using Ultralytics YOLO API
  - Map YOLO class IDs to FabriX defect taxonomy
  - Generate Grad-CAM heatmap for each detection
  - Emit results via asyncio Queue to WebSocket broadcaster
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DefectDetection:
    bbox: tuple[float, float, float, float]  # x1, y1, x2, y2 (normalized)
    class_name: str
    confidence: float
    severity: str  # 'low' | 'medium' | 'high' | 'critical'


class DefectDetector:
    """Placeholder — implement in Phase 2."""

    def __init__(self, model_path: Path):
        self.model_path = model_path
        self.model: Any = None  # Will be Ultralytics YOLO instance

    def load(self) -> None:
        """Load model weights from disk."""
        raise NotImplementedError

    def predict(self, frame) -> list[DefectDetection]:
        """Run inference on a single frame. Returns list of detections."""
        raise NotImplementedError
