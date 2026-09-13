"""Reproducible real-weight visual smoke test, not a dataset accuracy benchmark."""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ai.inference.run_detection import (
    CLASS_NAMES,
    ROOT,
    FabricDetector,
    annotate,
    detect_image,
)
from edge.stream_handler import process_video


def verify(output: Path) -> dict:
    """Use first two strong real val examples per populated class, without tuning."""
    output.mkdir(parents=True, exist_ok=False)
    data = ROOT / "ai/datasets/processed"
    rows = [
        json.loads(line) for line in (data / "manifest.jsonl").read_text().splitlines()
    ]
    detector = FabricDetector()
    panels, selected, results, frames = [], [], [], []
    for name in CLASS_NAMES[:7]:
        candidates = sorted(
            (
                r
                for r in rows
                if r["track"] == "multiclass"
                and r["split"] == "val"
                and r["class_name"] == name
                and not r["augmented"]
                and not r.get("synthetic")
                and r["source"] != "rmshashi_fabric_defect"
            ),
            key=lambda r: r["image"],
        )[:2]
        if len(candidates) != 2:
            raise ValueError(f"Need two real validation samples for {name}")
        tiles = []
        for index, row in enumerate(candidates):
            image = cv2.imread(str(data / row["image"]))
            report = detect_image(
                data / row["image"], output / f"{name}_{index}.png", detector
            )
            truth = []
            for line in (data / row["label"]).read_text().splitlines():
                cls, x, y, w, h = map(float, line.split())
                truth.append(
                    {
                        "class_name": CLASS_NAMES[int(cls)],
                        "confidence": 1.0,
                        "xyxy": [
                            (x - w / 2) * 640,
                            (y - h / 2) * 640,
                            (x + w / 2) * 640,
                            (y + h / 2) * 640,
                        ],
                    }
                )
            for label, rendered in (
                ("GROUND TRUTH", annotate(image, truth)),
                ("PREDICTION conf>=0.25", cv2.imread(report["output"])),
            ):
                tile = cv2.resize(rendered, (320, 320))
                cv2.rectangle(tile, (0, 0), (319, 23), (0, 0, 0), -1)
                cv2.putText(
                    tile,
                    label,
                    (4, 16),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 255, 255),
                    1,
                )
                tiles.append(tile)
            selected.append(
                {
                    "image": row["image"],
                    "class_name": name,
                    "split": "val",
                    "source": row["source"],
                }
            )
            results.append(report)
            frames.extend([image, image])
        panels.append(np.concatenate(tiles, axis=1))
    cv2.imwrite(str(output / "comparison.jpg"), np.concatenate(panels))
    video = output / "real_validation_slideshow.avi"
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 4, (640, 640))
    try:
        if not writer.isOpened():
            raise OSError("Cannot create validation slideshow")
        for frame in frames:
            writer.write(frame)
    finally:
        writer.release()
    video_report = process_video(video, output / "annotated.mp4", detector)
    capture = cv2.VideoCapture(video_report["output"])
    try:
        for index in (0, 8, 20, 24):
            capture.set(cv2.CAP_PROP_POS_FRAMES, index)
            ok, frame = capture.read()
            if not ok:
                raise OSError(f"Cannot read annotated review frame {index}")
            cv2.imwrite(str(output / f"video_frame_{index}.png"), frame)
    finally:
        capture.release()
    report = {
        "scope": "14 real validation images; 28-frame slideshow, not camera footage or mAP evaluation",
        "selected": selected,
        "images": results,
        "video": video_report,
    }
    (output / "verification.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    if not sum(len(r["detections"]) for r in results) or video_report["boxes"] == 0:
        raise AssertionError("Real checkpoint produced no detections")
    print(
        json.dumps(
            {
                "image_detections": [len(r["detections"]) for r in results],
                "video": video_report,
                "review": str(output / "comparison.jpg"),
            },
            indent=2,
        )
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/inference_v2")
    verify(parser.parse_args().output)
