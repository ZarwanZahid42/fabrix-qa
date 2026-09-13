"""Bounded, every-frame local video annotation with the shared prototype detector.

No camera reconnect, audio preservation, tracking, ROI or live backend integration
is implied. Failed encodes remain in a named staging folder for diagnosis.
"""

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path

import cv2

# Support both `python -m edge.stream_handler` and direct script invocation.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ai.inference.run_detection import DEFAULT_WEIGHTS, FabricDetector, annotate


def process_video(
    source: Path, output: Path, detector: FabricDetector | None = None
) -> dict:
    """Load once, process one frame at a time, preserve frame rate and dimensions."""
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if output.exists() or source == output:
        raise FileExistsError(output)
    if output.suffix.lower() not in (".mp4", ".avi"):
        raise ValueError("Use .mp4 (mp4v) or .avi (MJPG) output")
    detector = detector if detector is not None else FabricDetector()
    capture = cv2.VideoCapture(str(source))
    writer = None
    frames = detected_frames = total_boxes = 0
    try:
        if not capture.isOpened():
            raise ValueError(f"Cannot open video: {source}")
        fps = capture.get(cv2.CAP_PROP_FPS)
        if not math.isfinite(fps) or fps <= 0:
            raise ValueError("Video lacks a valid frame rate; refusing guessed timing")
        expected = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        ok, frame = capture.read()
        if not ok:
            raise ValueError("Video has no decodable frames")
        height, width = frame.shape[:2]
        if width % 2 or height % 2:
            raise ValueError(
                "Encoder requires even dimensions; refusing silent cropping"
            )
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix="video_stage_", dir=output.parent))
        partial = staging / output.name
        codec = "mp4v" if output.suffix.lower() == ".mp4" else "MJPG"
        writer = cv2.VideoWriter(
            str(partial), cv2.VideoWriter_fourcc(*codec), fps, (width, height)
        )
        if not writer.isOpened():
            raise OSError(f"Video encoder {codec} unavailable; staging: {staging}")
        with (staging / "frames.jsonl").open("x", encoding="utf-8") as log:
            while ok:
                if frame.shape[:2] != (height, width):
                    raise ValueError("Frame dimensions changed mid-stream")
                detections = detector.predict(frame)
                writer.write(annotate(frame, detections))
                log.write(
                    json.dumps(
                        {
                            "frame_index": frames,
                            "time_seconds": frames / fps,
                            "detections": detections,
                        }
                    )
                    + "\n"
                )
                frames += 1
                detected_frames += bool(detections)
                total_boxes += len(detections)
                ok, frame = capture.read()
        if expected > 0 and frames != expected:
            raise ValueError(
                f"Truncated/decode failure: expected {expected}, read {frames}; {staging}"
            )
        writer.release()
        writer = None
        # Decode every output frame: VideoWriter.write has no success return value.
        check = cv2.VideoCapture(str(partial))
        count = 0
        try:
            while True:
                readable, saved = check.read()
                if not readable:
                    break
                if saved.shape[:2] != (height, width):
                    raise OSError("Encoded dimensions do not match input")
                count += 1
            if count != frames or abs(check.get(cv2.CAP_PROP_FPS) - fps) > 0.01:
                raise OSError(f"Encoded video verification failed; staging: {staging}")
        finally:
            check.release()
        if output.exists():
            raise FileExistsError(output)
        partial.rename(output)
        report = {
            **detector.provenance(),
            "input": str(source),
            "output": str(output),
            "frames": frames,
            "fps": fps,
            "width": width,
            "height": height,
            "detected_frames": detected_frames,
            "boxes": total_boxes,
            "audio_preserved": False,
            "frame_log": str(staging / "frames.jsonl"),
        }
        (staging / "summary.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        return report
    finally:
        capture.release()
        if writer is not None:
            writer.release()


def main() -> None:
    """Annotate an input video with the same checkpoint and image inference path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--weights", type=Path, default=DEFAULT_WEIGHTS)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()
    detector = FabricDetector(args.weights, device=args.device, confidence=args.conf)
    print(json.dumps(process_video(args.source, args.output, detector), indent=2))


if __name__ == "__main__":
    main()
