"""Load both generated dataset configs and actual samples without training."""

import argparse
import json
import os
from pathlib import Path


def check(output: Path) -> None:
    """Scan every multiclass label and representative anomaly labels via YOLO."""
    # Ultralytics tests the parent directory before creating its config folder.
    # Create it first so its fallback cannot write settings into the repo root.
    for name in ("ultralytics", "matplotlib"):
        (output / "_toolcache" / name).mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("YOLO_CONFIG_DIR", str(output / "_toolcache" / "ultralytics"))
    os.environ.setdefault("MPLCONFIGDIR", str(output / "_toolcache" / "matplotlib"))
    from ultralytics import YOLO
    from ultralytics.data.dataset import YOLODataset
    from ultralytics.data.utils import check_det_dataset

    model = YOLO("yolov8n.yaml")  # Bundled model architecture; no weights/download.
    assert model.task == "detect"
    rows = [
        json.loads(line)
        for line in (output / "manifest.jsonl").read_text().splitlines()
    ]
    results = {}
    for prefix, track in (("", "multiclass"), ("anomaly", "anomaly")):
        data = check_det_dataset(str(output / prefix / "data.yaml"), autodownload=False)
        for split in ("train", "val", "test"):
            expected = [
                r
                for r in rows
                if r["track"] == track
                and r["split"] == split
                and r["annotation_kind"] != "classification_only"
            ]
            path = data[split]
            if track == "anomaly":
                # All anomaly files were independently decoded by --verify.
                # A bounded real loader check samples both binary outcomes here.
                expected = [r for r in expected if r["classes"]][:8] + [
                    r for r in expected if not r["classes"]
                ][:8]
                sample_list = output / "anomaly" / f"loader_smoke_{split}.txt"
                sample_list.write_text(
                    "".join(str(output / r["image"]) + "\n" for r in expected),
                    encoding="utf-8",
                )
                path = str(sample_list)
            dataset = YOLODataset(
                img_path=path,
                data=data,
                imgsz=640,
                augment=False,
                cache=False,
                batch_size=2,
                task="detect",
                prefix=f"{track}/{split}: ",
            )
            if len(dataset) != len(expected):
                raise ValueError(f"Ultralytics rejected images in {track}/{split}")
            actual_boxes = sum(len(label["cls"]) for label in dataset.labels)
            expected_boxes = sum(r["box_count"] for r in expected)
            if actual_boxes != expected_boxes:
                raise ValueError(
                    f"Ultralytics changed box counts in {track}/{split}: {actual_boxes}!={expected_boxes}"
                )
            sample = dataset[0]
            assert tuple(sample["img"].shape) == (3, 640, 640)
            results[f"{track}/{split}"] = {
                "loaded_images": len(dataset),
                "loaded_boxes": actual_boxes,
                "tensor_shape": list(sample["img"].shape),
            }
    (output / "ultralytics-verification.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "datasets" / "processed",
    )
    check(parser.parse_args().output.resolve())
