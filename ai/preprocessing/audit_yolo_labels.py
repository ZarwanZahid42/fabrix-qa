"""Read-only audit of every semantic YOLO label, including tiny-box diagnostics."""

import argparse
import hashlib
import json
import math
import os
from collections import Counter
from pathlib import Path

import yaml


def check_box(line: str, class_count: int) -> list[str]:
    """Return all basic geometry failures; do not discard or repair annotations."""
    fields = line.split()
    if len(fields) != 5:
        return ["expected five fields"]
    try:
        cls, x, y, w, h = map(float, fields)
    except ValueError:
        return ["nonnumeric field"]
    if not all(math.isfinite(v) for v in (cls, x, y, w, h)):
        return ["NaN/inf field"]
    errors = []
    if not cls.is_integer() or not 0 <= cls < class_count:
        errors.append("invalid class ID")
    if not (0 <= x <= 1 and 0 <= y <= 1):
        errors.append("center outside [0,1]")
    if not (0 < w <= 1 and 0 < h <= 1):
        errors.append("width/height outside (0,1]")
    if min(x - w / 2, y - h / 2) < -1e-8 or max(x + w / 2, y + h / 2) > 1 + 1e-8:
        errors.append("box corners outside image (tolerance 1e-8)")
    return errors


def audit(output: Path) -> dict:
    """Scan all .txt labels, report source/split counts and exact bad rows."""
    config = yaml.safe_load((output / "data.yaml").read_text(encoding="utf-8"))
    names = config["names"]
    if config.get("nc", len(names)) != len(names):
        raise ValueError("YAML nc/names mismatch")
    records = {}
    with (output / "manifest.jsonl").open(encoding="utf-8") as stream:
        for text in stream:
            row = json.loads(text)
            if (
                row["track"] == "multiclass"
                and row["label"]
                and row["annotation_kind"] != "classification_only"
            ):
                records[row["label"]] = row
    files = sorted((output / "labels").rglob("*.txt"))
    if not files:
        raise ValueError("No semantic label files found")
    counts, errors, tiny = Counter(), [], []
    minimum_pixels = [640.0, 640.0]
    for path in files:
        key = path.relative_to(output).as_posix()
        row = records.get(key)
        source = row["source"] if row else "unmanifested"
        if row and row.get("synthetic"):
            source += "/" + row["class_name"]
        group = f"{path.parent.name}/{source}"
        counts[group + "/files"] += 1
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines:
            counts[group + "/background_files"] += 1
        if row is None:
            errors.append({"label": key, "reasons": ["unmanifested label"]})
        for number, line in enumerate(lines, 1):
            counts[group + "/boxes"] += 1
            bad = check_box(line, len(names))
            if bad:
                errors.append(
                    {"label": key, "line": number, "value": line, "reasons": bad}
                )
                continue
            _, _, _, w, h = map(float, line.split())
            minimum_pixels = [
                min(minimum_pixels[0], w * 640),
                min(minimum_pixels[1], h * 640),
            ]
            if min(w, h) * 640 < 1:
                tiny.append(
                    {
                        "label": key,
                        "line": number,
                        "source": source,
                        "wh_pixels": [w * 640, h * 640],
                    }
                )
    missing = set(records) - {p.relative_to(output).as_posix() for p in files}
    errors.extend(
        {"label": key, "reasons": ["missing label file"]} for key in sorted(missing)
    )
    return {
        "scope": "Every .txt file under semantic labels/; no files repaired or removed",
        "label_files": len(files),
        "boxes": sum(v for k, v in counts.items() if k.endswith("/boxes")),
        "invalid_count": len(errors),
        "invalid": errors,
        "counts": dict(counts),
        "minimum_wh_pixels_at_640": minimum_pixels,
        "subpixel_box_count": len(tiny),
        "subpixel_boxes": tiny,
        "note": "Positive subpixel boxes are warnings, not zero-sized labels or proof of infinite training loss.",
    }


def probe_ciou(output: Path) -> dict:
    """Bounded CPU float32 target-geometry probe, not actual GPU/AMP training."""
    for key, name in (
        ("YOLO_CONFIG_DIR", "ultralytics"),
        ("MPLCONFIGDIR", "matplotlib"),
    ):
        path = output.resolve() / "_toolcache" / name
        path.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault(key, str(path))
    import torch
    from ultralytics.utils.metrics import bbox_iou

    boxes = []
    for path in (output / "labels/train").rglob("*.txt"):
        for line in path.read_text().splitlines():
            _, x, y, w, h = map(float, line.split())
            boxes.append([x - w / 2, y - h / 2, x + w / 2, y + h / 2])
    torch.set_num_threads(1)
    checks = []
    for stride in (8, 16, 32):
        target = torch.tensor(boxes, dtype=torch.float32) * 640 / stride
        for offset in (0.0, 0.01, 0.5):
            prediction = (target + offset).clone().requires_grad_(True)
            loss = 1 - bbox_iou(prediction, target, xywh=False, CIoU=True)
            loss.mean().backward()
            checks.append(
                {
                    "stride": stride,
                    "offset": offset,
                    "forward_finite": bool(torch.isfinite(loss).all()),
                    "gradient_finite": bool(torch.isfinite(prediction.grad).all()),
                }
            )
    return {
        "scope": "CPU float32 CIoU on every train target with controlled predictions; not model/AMP reproduction",
        "manifest_sha256": hashlib.sha256(
            (output / "manifest.jsonl").read_bytes()
        ).hexdigest(),
        "train_boxes": len(boxes),
        "torch": torch.__version__,
        "checks": checks,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "datasets/processed",
    )
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--probe-ciou",
        action="store_true",
        help="Also run a limited CPU float32 target-geometry probe",
    )
    args = parser.parse_args()
    report = audit(args.output)
    if args.probe_ciou and not report["invalid_count"]:
        report["ciou_probe"] = probe_ciou(args.output)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    probe_failed = any(
        not c["forward_finite"] or not c["gradient_finite"]
        for c in report.get("ciou_probe", {}).get("checks", [])
    )
    raise SystemExit(bool(report["invalid_count"] or probe_failed))
