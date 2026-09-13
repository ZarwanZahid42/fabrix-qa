"""Local image/frame inference with the supplied FabriX-QA prototype v2 checkpoint."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WEIGHTS = ROOT / "ai/models/best.pt"
CLASS_NAMES = (
    "hole",
    "weave_error",
    "stain",
    "foreign_object",
    "crease",
    "edge_damage",
    "pattern_break",
    "aitex_unmapped",
    "tilda_unmapped",
)


class FabricDetector:
    """Load once, enforce taxonomy, and return original-frame pixel coordinates.

    Only load trusted PyTorch checkpoints. Missing weights never trigger a
    pretrained download or fallback. Confidence is not a calibrated grade.
    """

    def __init__(
        self,
        weights: Path = DEFAULT_WEIGHTS,
        *,
        device: str = "cpu",
        confidence: float = 0.25,
        iou: float = 0.7,
    ) -> None:
        self.weights = Path(weights).resolve()
        if not self.weights.is_file():
            raise FileNotFoundError(f"Supply the trained checkpoint: {self.weights}")
        if not (
            math.isfinite(confidence)
            and 0 <= confidence <= 1
            and math.isfinite(iou)
            and 0 < iou <= 1
        ):
            raise ValueError("Require confidence in [0,1] and IoU in (0,1]")
        for key, name in (
            ("YOLO_CONFIG_DIR", "ultralytics"),
            ("MPLCONFIGDIR", "matplotlib"),
        ):
            if key not in os.environ:
                cache = ROOT / "artifacts/toolcache" / name
                cache.mkdir(parents=True, exist_ok=True)
                os.environ[key] = str(cache)
        from ultralytics import YOLO

        self.model = YOLO(str(self.weights), task="detect")
        if self.model.task != "detect" or self.model.names != dict(
            enumerate(CLASS_NAMES)
        ):
            raise ValueError(f"Checkpoint task/taxonomy mismatch: {self.model.names}")
        self.sha256 = hashlib.sha256(self.weights.read_bytes()).hexdigest()
        self.device, self.confidence, self.iou = device, confidence, iou

    def predict(self, frame: np.ndarray) -> list[dict]:
        """Accept one uint8 BGR frame; no file writes, resizing distortion or queue."""
        if (
            not isinstance(frame, np.ndarray)
            or frame.dtype != np.uint8
            or frame.ndim != 3
            or frame.shape[2] != 3
            or frame.size == 0
        ):
            raise ValueError("Expected a nonempty HxWx3 uint8 BGR frame")
        result = self.model.predict(
            source=frame,
            imgsz=640,
            rect=False,
            conf=self.confidence,
            iou=self.iou,
            device=self.device,
            verbose=False,
            save=False,
        )[0]
        detections = []
        height, width = frame.shape[:2]
        for x1, y1, x2, y2, score, cls in result.boxes.data.cpu().tolist():
            if not all(math.isfinite(v) for v in (x1, y1, x2, y2, score, cls)):
                raise ValueError("Nonfinite model prediction")
            if (
                cls != int(cls)
                or not 0 <= cls < len(CLASS_NAMES)
                or not 0 <= score <= 1
                or not 0 <= x1 < x2 <= width
                or not 0 <= y1 < y2 <= height
            ):
                raise ValueError("Invalid class/confidence/original-frame box")
            detections.append(
                {
                    "class_id": int(cls),
                    "class_name": CLASS_NAMES[int(cls)],
                    "confidence": score,
                    "xyxy": [x1, y1, x2, y2],
                }
            )
        return detections

    def provenance(self) -> dict:
        """Small local prototype record, not the future production event contract."""
        return {
            "model": str(self.weights),
            "sha256": self.sha256,
            "class_names": list(CLASS_NAMES),
            "device": self.device,
            "confidence": self.confidence,
            "iou": self.iou,
            "imgsz": 640,
            "coordinates": "xyxy pixels in original input frame",
        }


def annotate(frame: np.ndarray, detections: list[dict]) -> np.ndarray:
    """Draw readable class/confidence overlays on a copy; no font downloads/GUI."""
    output = frame.copy()
    height, width = frame.shape[:2]
    for detection in detections:
        x1, y1, x2, y2 = map(round, detection["xyxy"])
        color = (40, 220, 255)
        cv2.rectangle(
            output, (x1, y1), (min(width - 1, x2), min(height - 1, y2)), color, 2
        )
        label = f"{detection['class_name']} {detection['confidence']:.2f}"
        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        left = max(0, min(x1, width - tw - 4))
        top = max(0, min(y1 - th - baseline - 6, height - th - baseline - 6))
        cv2.rectangle(
            output, (left, top), (left + tw + 4, top + th + baseline + 6), color, -1
        )
        cv2.putText(
            output,
            label,
            (left + 2, top + th + 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )
    return output


def detect_image(source: Path, output: Path, detector: FabricDetector) -> dict:
    """Save one annotated image, refusing to overwrite any existing file."""
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if output.exists() or source == output:
        raise FileExistsError(output)
    if output.suffix.lower() not in (".png", ".jpg", ".jpeg"):
        raise ValueError("Image output must be PNG or JPEG")
    frame = cv2.imread(str(source))
    if frame is None:
        raise ValueError(f"Cannot decode image: {source}")
    detections = detector.predict(frame)
    ok, encoded = cv2.imencode(output.suffix, annotate(frame, detections))
    if not ok:
        raise OSError("Cannot encode annotated image")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(encoded.tobytes())
    return {
        **detector.provenance(),
        "input": str(source),
        "output": str(output),
        "detections": detections,
    }


def main() -> None:
    """Image CLI; default checkpoint is independent of the working directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--weights", type=Path, default=DEFAULT_WEIGHTS)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()
    detector = FabricDetector(args.weights, device=args.device, confidence=args.conf)
    print(json.dumps(detect_image(args.source, args.output, detector), indent=2))


if __name__ == "__main__":
    main()
