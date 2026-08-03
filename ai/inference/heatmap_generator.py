"""
Heatmap Generator — Grad-CAM Visualization
============================================
Generates Gradient-weighted Class Activation Maps (Grad-CAM) for detected defects.
Heatmaps are saved to MongoDB as base64-encoded PNG overlays.

TODO:
  - Implement GradCAMGenerator for the defect classifier model
  - Add overlay blending logic (heatmap + original frame)
  - Serialize heatmap to base64 and store metadata in MongoDB
"""


class HeatmapGenerator:
    """Placeholder — implement in Phase 2."""

    def generate(self, frame, model, class_idx: int) -> bytes:
        """Generate Grad-CAM heatmap. Returns PNG bytes."""
        raise NotImplementedError
