"""
Module 1 — Region of Interest (ROI) Selector
==============================================
Responsible for:
  - Defining a polygonal or rectangular ROI on the fabric frame
  - Cropping / masking raw frames to the ROI before passing to AI
  - Supporting both manual GUI selection and saved presets

TODO:
  - Implement ROISelector using OpenCV's selectROI or custom polygon mask
  - Persist selected ROI coordinates to a config file (JSON)
  - Add unit tests in tests/edge/test_roi_selector.py
"""

from __future__ import annotations
import json
from pathlib import Path


class ROISelector:
    """Placeholder — to be implemented in Phase 2."""

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path
        self._roi: dict | None = None

    def select(self, frame):
        """Interactively select ROI from a frame. Returns (x, y, w, h)."""
        raise NotImplementedError

    def apply(self, frame):
        """Crop frame to saved ROI."""
        raise NotImplementedError

    def save(self) -> None:
        if self._roi and self.config_path:
            self.config_path.write_text(json.dumps(self._roi, indent=2))

    def load(self) -> None:
        if self.config_path and self.config_path.exists():
            self._roi = json.loads(self.config_path.read_text())
