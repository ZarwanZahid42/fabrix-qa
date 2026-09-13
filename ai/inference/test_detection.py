"""Deterministic boundary/video tests; real checkpoint checks use verify_detection."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import cv2
import numpy as np

from ai.inference.run_detection import (
    CLASS_NAMES,
    FabricDetector,
    annotate,
    detect_image,
)
from edge.stream_handler import process_video


class StubDetector:
    """Test fixture only, not a substitute for real-weight verification."""

    def predict(self, frame):
        return [
            {
                "class_id": 0,
                "class_name": "hole",
                "confidence": 0.9,
                "xyxy": [10, 20, 40, 50],
            }
        ]

    def provenance(self):
        return {"model": "TEST FIXTURE"}


class DetectionTests(unittest.TestCase):
    def test_missing_weights_and_bad_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "best.pt"
            with self.assertRaises(FileNotFoundError):
                FabricDetector(path)
            path.write_bytes(b"fixture")
            with self.assertRaises(ValueError):
                FabricDetector(path, confidence=float("nan"))

    def test_wrong_checkpoint_taxonomy_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "best.pt"
            path.write_bytes(b"fixture")
            with patch(
                "ultralytics.YOLO",
                return_value=SimpleNamespace(task="detect", names={0: "person"}),
            ), self.assertRaises(ValueError):
                FabricDetector(path)

    def test_frame_boundaries_and_nonfinite_prediction(self):
        detector = FabricDetector.__new__(FabricDetector)
        detector.confidence, detector.iou, detector.device = 0.25, 0.7, "cpu"
        with self.assertRaises(ValueError):
            detector.predict(np.zeros((20, 20), np.uint8))

        class Data:
            def cpu(self):
                return self

            def tolist(self):
                return [[1, 2, 4, 5, float("nan"), 0]]

        detector.model = SimpleNamespace(
            predict=lambda **kwargs: [
                SimpleNamespace(boxes=SimpleNamespace(data=Data()))
            ]
        )
        with self.assertRaises(ValueError):
            detector.predict(np.zeros((20, 20, 3), np.uint8))

    def test_overlay_and_image_no_overwrite(self):
        frame = np.zeros((64, 96, 3), np.uint8)
        self.assertTrue(np.array_equal(frame, annotate(frame, [])))
        self.assertTrue(annotate(frame, StubDetector().predict(frame)).any())
        self.assertFalse(frame.any())
        self.assertEqual(len(CLASS_NAMES), 9)
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "in.png", Path(directory) / "out.png"
            cv2.imwrite(str(source), frame)
            report = detect_image(source, output, StubDetector())
            self.assertEqual(report["detections"][0]["class_name"], "hole")
            with self.assertRaises(FileExistsError):
                detect_image(source, output, StubDetector())

    def test_video_all_frames_timing_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "in.avi", Path(directory) / "out.avi"
            writer = cv2.VideoWriter(
                str(source), cv2.VideoWriter_fourcc(*"MJPG"), 5, (96, 64)
            )
            self.assertTrue(writer.isOpened())
            for _ in range(3):
                writer.write(np.zeros((64, 96, 3), np.uint8))
            writer.release()
            report = process_video(source, output, StubDetector())
            self.assertEqual(
                (report["frames"], report["fps"], report["boxes"]), (3, 5, 3)
            )
            self.assertEqual(len(Path(report["frame_log"]).read_text().splitlines()), 3)
            with self.assertRaises(FileExistsError):
                process_video(source, output, StubDetector())
            with self.assertRaises(FileNotFoundError):
                process_video(Path(directory) / "missing.avi", output, StubDetector())


if __name__ == "__main__":
    unittest.main()
