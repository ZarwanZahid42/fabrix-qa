"""Build reproducible multiclass YOLO and separate ZJU anomaly datasets.

See ai/datasets/README.md for researched mappings and annotation limitations.
No downloads, model training, or raw-data mutations are performed by this module.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import shutil
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from importlib.metadata import version
from pathlib import Path
from typing import Any

os.environ.setdefault("NO_ALBUMENTATIONS_UPDATE", "1")

import albumentations as A
import cv2
import numpy as np
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / "datasets"
NAMES = [
    "hole",
    "weave_error",
    "stain",
    "foreign_object",
    "crease",
    "edge_damage",
    "pattern_break",
    "aitex_unmapped",
    "tilda_unmapped",
]
AITEX = {
    "002": ("broken_end", "weave_error"),
    "006": ("broken_yarn", "weave_error"),
    "010": ("broken_pick", "weave_error"),
    "016": ("weft_curling", "weave_error"),
    "019": ("fuzzy_ball", "weave_error"),
    "022": ("cut_selvage", "edge_damage"),
    "023": ("crease", "crease"),
    "025": ("warp_ball", "weave_error"),
    "027": ("knots", "weave_error"),
    "029": ("contamination", "foreign_object"),
    "030": ("nep", "weave_error"),
    "036": ("weft_crack", "weave_error"),
}
TILDA = {0: "hole", 1: "foreign_object", 2: "stain", 3: "weave_error"}
SOURCES = ["rmshashi_fabric_defect", "aitex", "tilda_400", "zju_leaper", "mvtec_ad"]
SPLITS = ("train", "val", "test")
AITEX_TILING = {"size": 256, "stride": 192, "backgrounds_per_positive": 0.25}


def digest(data: bytes) -> str:
    """Return a stable SHA-256 digest for content identity and provenance."""
    return hashlib.sha256(data).hexdigest()


def load_rgb(path: Path) -> np.ndarray:
    """Decode every pixel; grayscale is expanded and EXIF is not auto-rotated.

    Labels describe stored pixel coordinates, so applying EXIF orientation alone
    would move images without moving boxes. Transparency is not a defect channel.
    """
    with Image.open(path) as image:
        image.load()
        return np.asarray(image.convert("RGB")).copy()


def load_mask(paths: list[str], shape: tuple[int, int]) -> np.ndarray:
    """OR luminance foreground from all masks, validating dimensions."""
    mask = np.zeros(shape, dtype=np.uint8)
    for name in paths:
        with Image.open(name) as image:
            part = np.asarray(image.convert("L"))
        if part.shape != shape:
            raise ValueError(
                f"Mask/image dimensions differ: {name}: {part.shape} != {shape}"
            )
        mask |= (part > 0).astype(np.uint8)
    return mask


def mask_boxes(mask: np.ndarray) -> list[list[float]]:
    """Return half-open XYXY rectangles around every 8-connected region."""
    count, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    return [
        [float(x), float(y), float(x + w), float(y + h)]
        for x, y, w, h, _ in stats[1:count]
    ]


def check_boxes(boxes: list, width: int, height: int) -> None:
    """Reject invalid geometry instead of silently clamping malformed labels."""
    for box in boxes:
        x1, y1, x2, y2 = box
        if not all(math.isfinite(float(v)) for v in box):
            raise ValueError(f"Non-finite box: {box}")
        if not (0 <= x1 < x2 <= width + 1e-5 and 0 <= y1 < y2 <= height + 1e-5):
            raise ValueError(f"Invalid box {box} for {width}x{height}")


def reconcile_tilda(
    boxes: list, classes: list[int], mask: np.ndarray
) -> tuple[list, list[int], dict]:
    """Expand supplied boxes to cover linked mask regions; preserve unmasked boxes.

    Visual inspection found truncated thread boxes and a plausible extra hole
    missing from a mask. Neither annotation is discarded: mask components join
    the best-overlapping box, or form an extra box with the image's sole class.
    """
    if len(set(classes)) != 1 or not mask.any():
        raise ValueError(
            "TILDA reconciliation requires one known image class and a nonempty mask"
        )
    result = [list(b) for b in boxes]
    count, regions, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    linked = set()
    added = 0
    for component in range(1, count):
        x, y, w, h, _ = stats[component]
        rect = [float(x), float(y), float(x + w), float(y + h)]
        overlaps = []
        for x1, y1, x2, y2 in boxes:
            patch = regions[
                max(0, math.floor(y1)) : min(mask.shape[0], math.ceil(y2)),
                max(0, math.floor(x1)) : min(mask.shape[1], math.ceil(x2)),
            ]
            overlaps.append(int((patch == component).sum()))
        if max(overlaps, default=0):
            linked.update(i for i, overlap in enumerate(overlaps) if overlap > 0)
            best = overlaps.index(max(overlaps))
            b = result[best]
            result[best] = [
                min(b[0], rect[0]),
                min(b[1], rect[1]),
                max(b[2], rect[2]),
                max(b[3], rect[3]),
            ]
        else:
            result.append(rect)
            added += 1
    return (
        result,
        classes + [classes[0]] * added,
        {
            "expanded_boxes": sum(a != b for a, b in zip(boxes, result)),
            "added_mask_components": added,
            "retained_boxes_without_mask_overlap": len(boxes) - len(linked),
        },
    )


def letterbox(
    image: np.ndarray, boxes: list, mask: np.ndarray | None = None, size: int = 640
) -> tuple[np.ndarray, list, np.ndarray | None, dict]:
    """Use rounded resized dimensions for exact image/box coordinate agreement."""
    h, w = image.shape[:2]
    scale = min(size / w, size / h)
    nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
    left, top = (size - nw) // 2, (size - nh) // 2
    canvas = np.full((size, size, 3), 114, dtype=np.uint8)
    canvas[top : top + nh, left : left + nw] = cv2.resize(
        image, (nw, nh), interpolation=cv2.INTER_AREA
    )
    mapped = [
        [x1 * nw / w + left, y1 * nh / h + top, x2 * nw / w + left, y2 * nh / h + top]
        for x1, y1, x2, y2 in boxes
    ]
    transformed = None
    if mask is not None:
        transformed = np.zeros((size, size), dtype=np.uint8)
        # Occupancy downsampling preserves thin defects that nearest-neighbor
        # sampling can erase. Boxes retain their exact subpixel coordinates.
        interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_NEAREST
        transformed[top : top + nh, left : left + nw] = (
            cv2.resize(mask.astype(np.float32), (nw, nh), interpolation=interpolation)
            > 0
        ).astype(np.uint8)
    return (
        canvas,
        mapped,
        transformed,
        {"original_wh": [w, h], "resized_wh": [nw, nh], "pad_lt": [left, top]},
    )


def to_yolo(boxes: list, classes: list[int], size: int = 640) -> str:
    """Serialize accurate normalized boxes, including subpixel small defects."""
    check_boxes(boxes, size, size)
    if len(boxes) != len(classes):
        raise ValueError("Class/box count differs")
    return "".join(
        f"{int(c)} {(x1+x2)/2/size:.10f} {(y1+y2)/2/size:.10f} "
        f"{(x2-x1)/size:.10f} {(y2-y1)/size:.10f}\n"
        for c, (x1, y1, x2, y2) in zip(classes, boxes)
    )


def read_yolo(path: Path, width: int, height: int) -> tuple[list, list[int]]:
    """Validate a YOLO file and return pixel rectangles and integer IDs."""
    boxes, classes = [], []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 5:
            raise ValueError(f"Malformed YOLO row: {path}:{number}")
        c, x, y, w, h = map(float, parts)
        if c != int(c) or c < 0:
            raise ValueError(f"Invalid class: {path}:{number}")
        boxes.append(
            [
                (x - w / 2) * width,
                (y - h / 2) * height,
                (x + w / 2) * width,
                (y + h / 2) * height,
            ]
        )
        classes.append(int(c))
    # Decimal-export rounding in TILDA can overshoot an image edge by <0.001px.
    # Correct only that numerical tolerance; substantive invalid geometry fails.
    for box in boxes:
        if all(math.isfinite(v) for v in box) and (
            min(box[0], box[1]) >= -0.001
            and box[2] <= width + 0.001
            and box[3] <= height + 0.001
        ):
            box[0], box[1] = max(0.0, box[0]), max(0.0, box[1])
            box[2], box[3] = min(float(width), box[2]), min(float(height), box[3])
    check_boxes(boxes, width, height)
    return boxes, classes


def scan_sources(raw: Path) -> list[dict[str, Any]]:
    """Inspect actual structures before any image conversion; retain raw labels."""
    records: list[dict[str, Any]] = []

    def add(source: str, path: Path, label: str, **extra: Any) -> None:
        rel = path.relative_to(raw).as_posix()
        records.append(
            {
                "source": source,
                "raw": rel,
                "path": str(path),
                "id": source + "_" + digest(rel.encode())[:20],
                "class_name": label,
                "track": "multiclass",
                "masks": [],
                "annotation_kind": "mask",
                "native_split": None,
                **extra,
            }
        )

    for source in SOURCES:
        directory = raw / source
        if not directory.is_dir() or not any(directory.iterdir()):
            raise ValueError(f"Missing/empty source: {directory}")
    base = raw / SOURCES[0] / "Data Set"
    folder_map = {
        "hole": "hole",
        "horizontal": "weave_error",
        "verticle": "weave_error",
        "captured/Hole": "hole",
        "captured/Lines": "weave_error",
    }
    for path in sorted(base.rglob("*.jpg")):
        folder = path.parent.relative_to(base).as_posix()
        if folder not in folder_map:
            raise ValueError(f"Unknown rmshashi folder: {folder}")
        add(
            SOURCES[0],
            path,
            folder_map[folder],
            raw_label=folder,
            normalized_source_label="vertical" if folder == "verticle" else folder,
            annotation_kind="weak_full_image",
        )

    base = raw / "aitex"
    for path in sorted((base / "Defect_images").glob("*.png")):
        code = path.stem.split("_")[1]
        name, cls = AITEX.get(code, (code, "aitex_unmapped"))
        masks = sorted((base / "Mask_images").glob(path.stem + "_mask*.png"))
        kind = "mask" if masks else "classification_only"
        add(
            "aitex",
            path,
            cls,
            raw_label=code,
            documented_label=name,
            mapping_status="researched" if code in AITEX else "unmapped/bucketed",
            annotation_kind=kind,
            masks=[str(p) for p in masks],
        )
    for path in sorted((base / "NODefect_images").rglob("*.png")):
        add("aitex", path, "normal", raw_label="000", annotation_kind="normal")

    base = raw / "tilda_400"
    for path in sorted((base / "images").glob("*.tif")):
        label = base / "labels" / (path.stem + ".txt")
        mask = base / "masks" / (path.stem + ".png")
        if not label.is_file() or not mask.is_file():
            raise ValueError(f"Missing TILDA annotation: {path}")
        ids = sorted(
            {
                int(line.split()[0])
                for line in label.read_text().splitlines()
                if line.strip()
            }
        )
        names = sorted({TILDA.get(c, "tilda_unmapped") for c in ids})
        add(
            "tilda_400",
            path,
            "+".join(names) if names else "normal",
            raw_label=ids,
            label_file=str(label),
            masks=[str(mask)],
            annotation_kind="yolo",
            mapping_status=(
                "researched" if all(c in TILDA for c in ids) else "unmapped/bucketed"
            ),
        )

    base = raw / "zju_leaper"
    split_data = json.loads((base / "ImageSets" / "total.json").read_text())
    native = {
        str(i): s for v in split_data.values() for s, ids in v.items() for i in ids
    }
    for path in sorted((base / "Images").glob("*.jpg")):
        xml_path = base / "Annotations" / "xmls" / (path.stem + ".xml")
        node = ET.parse(xml_path).getroot()
        flag = node.findtext("defective")
        if flag not in ("0", "1") or node.findtext("filename") != path.name:
            raise ValueError(f"Invalid ZJU annotation: {xml_path}")
        masks = []
        if flag == "1":
            mask_name = node.findtext("mask_filename")
            if not mask_name or Path(mask_name).name != mask_name:
                raise ValueError(f"Invalid mask reference: {xml_path}")
            masks = [str(base / "Annotations" / "masks" / mask_name)]
        native_boxes = [
            [int(b.findtext(k)) for k in ("xmin", "ymin", "xmax", "ymax")]
            for b in node.findall("bbox")
        ]
        add(
            "zju_leaper",
            path,
            "defective" if flag == "1" else "normal",
            raw_label=int(flag),
            track="anomaly",
            masks=masks,
            annotation_kind="mask" if flag == "1" else "normal",
            native_split=native.get(path.stem),
            pattern=node.findtext("pattern_id"),
            group=node.findtext("group_id"),
            xml_file=str(xml_path),
            native_boxes=native_boxes,
        )

    base = raw / "mvtec_ad"
    for category in ("carpet", "grid"):
        for split in ("train", "test"):
            for path in sorted((base / category / split).rglob("*.png")):
                subtype = path.parent.name
                masks = (
                    []
                    if subtype == "good"
                    else [
                        str(
                            base
                            / category
                            / "ground_truth"
                            / subtype
                            / (path.stem + "_mask.png")
                        )
                    ]
                )
                add(
                    "mvtec_ad",
                    path,
                    "normal" if subtype == "good" else "pattern_break",
                    raw_label=category + "/" + subtype,
                    masks=masks,
                    native_split=split,
                    annotation_kind="normal" if subtype == "good" else "mask",
                )
    for source in SOURCES:
        subset = [r for r in records if r["source"] == source]
        if not subset:
            raise ValueError(f"No expected images in {raw / source}")
        print(
            json.dumps(
                {
                    "source": source,
                    "images": len(subset),
                    "labels": dict(Counter(str(r["raw_label"]) for r in subset)),
                    "annotation_kinds": dict(
                        Counter(r["annotation_kind"] for r in subset)
                    ),
                }
            ),
            flush=True,
        )
    return records


def inspect_record(record: dict) -> dict:
    """Decode raw pixels, validate labels/masks, and hash all consumed inputs."""
    r = dict(record)
    image = load_rgb(Path(r["path"]))
    h, w = image.shape[:2]
    r["raw_sha256"] = digest(Path(r["path"]).read_bytes())
    r["pixel_sha256"] = digest(f"{w},{h},RGB:".encode() + image.tobytes())
    r["original_wh"] = [w, h]
    r["annotation_sha256"] = {
        str(p): digest(Path(p).read_bytes())
        for p in r["masks"] + [r[k] for k in ("label_file", "xml_file") if k in r]
    }
    mask = load_mask(r["masks"], (h, w)) if r["masks"] else None
    if r["source"] == "aitex" and r["annotation_kind"] == "mask" and not mask.any():
        r["annotation_kind"] = "classification_only"
        r["localization_exclusion"] = "bundled mask is entirely zero"
    cls = (
        0
        if r["track"] == "anomaly"
        else (NAMES.index(r["class_name"]) if r["class_name"] in NAMES else None)
    )
    kind = r["annotation_kind"]
    if kind == "weak_full_image":
        boxes, classes = [[0.0, 0.0, float(w), float(h)]], [cls]
    elif kind == "yolo":
        boxes, source_ids = read_yolo(Path(r["label_file"]), w, h)
        classes = [NAMES.index(TILDA.get(c, "tilda_unmapped")) for c in source_ids]
        r["supplied_boxes"] = [list(b) for b in boxes]
        r["supplied_class_ids"] = source_ids
        boxes, classes, r["tilda_mask_reconciliation"] = reconcile_tilda(
            boxes, classes, mask
        )
    elif kind == "mask":
        if mask is None or not mask.any():
            raise ValueError(f"Defective sample lacks nonempty mask: {r['raw']}")
        boxes = mask_boxes(mask)
        classes = [cls] * len(boxes)
    else:
        boxes, classes = [], []
    check_boxes(boxes, w, h)
    if "native_boxes" in r:
        check_boxes(r["native_boxes"], w, h)
    r["boxes"], r["classes"] = boxes, classes
    r["mask_pixels"] = int(mask.sum()) if mask is not None else None
    return r


def assign_splits(records: list[dict], seed: int) -> dict:
    """Group decoded duplicate images globally; stratify groups, not copies."""
    by_hash: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_hash[r["pixel_sha256"]].append(r)
    strata: dict[str, list[str]] = defaultdict(list)
    conflicts = []
    for key, group in sorted(by_hash.items()):
        strata_key = "|".join(
            sorted({r["source"] + ":" + r["class_name"] for r in group})
        )
        strata[strata_key].append(key)
        if len({r["class_name"] for r in group}) > 1:
            conflicts.append([r["raw"] for r in group])
    for stratum, hashes in sorted(strata.items()):
        random.Random(f"{seed}:{stratum}").shuffle(hashes)
        n = len(hashes)
        # Rare strata with <3 groups remain training-only, explicitly reported.
        nv = max(1, round(n * 0.1)) if n >= 3 else 0
        nt = max(1, round(n * 0.1)) if n >= 3 else 0
        for i, key in enumerate(hashes):
            split = "val" if i < nv else "test" if i < nv + nt else "train"
            for r in by_hash[key]:
                r["split"] = split
    return {
        "duplicate_groups": sum(len(v) > 1 for v in by_hash.values()),
        "duplicate_extra_images": sum(len(v) - 1 for v in by_hash.values()),
        "label_conflicts": conflicts,
        "stratum_group_counts": {k: len(v) for k, v in strata.items()},
    }


def augment(
    image: np.ndarray, boxes: list, classes: list, mask: np.ndarray | None, seed: int
) -> tuple[np.ndarray, list, list, np.ndarray | None]:
    """Transform image, box corners and mask together using a per-copy seed."""
    pipeline = A.Compose(
        [
            A.HorizontalFlip(p=0.5),
            A.RandomBrightnessContrast(
                brightness_limit=0.12, contrast_limit=0.12, p=0.8
            ),
            A.Rotate(
                limit=5, border_mode=cv2.BORDER_CONSTANT, fill=114, fill_mask=0, p=0.7
            ),
        ],
        bbox_params=A.BboxParams(
            format="pascal_voc",
            label_fields=["classes"],
            clip=True,
            min_area=0,
            min_visibility=0,
        ),
        seed=seed,
    )
    args = {"image": image, "bboxes": boxes, "classes": classes}
    if mask is not None:
        args["mask"] = mask
    result = pipeline(**args)
    if boxes and not len(result["bboxes"]):
        raise ValueError("Augmentation removed every defect box")
    return (
        result["image"],
        list(result["bboxes"]),
        [int(c) for c in result["classes"]],
        result.get("mask"),
    )


def save_image(path: Path, image: np.ndarray, mask: bool = False) -> None:
    """Check image encoder return values; never treat a failed write as success."""
    data = image * 255 if mask else cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    params = (
        [cv2.IMWRITE_PNG_COMPRESSION, 3] if mask else [cv2.IMWRITE_JPEG_QUALITY, 95]
    )
    if not cv2.imwrite(str(path), data, params):
        raise OSError(f"Image write failed: {path}")


def convert_record(r: dict, out: Path, seed: int) -> list[dict]:
    """Write one original plus train-only copies with shared parent/split."""
    if r["source"] == "aitex" and r["annotation_kind"] != "classification_only":
        return convert_aitex_tiles(r, out, seed)
    image = load_rgb(Path(r["path"]))
    mask = (
        load_mask(r["masks"], image.shape[:2])
        if r["masks"] and r["annotation_kind"] != "classification_only"
        else None
    )
    image, boxes, mask, transform = letterbox(image, r["boxes"], mask)
    prefix = "anomaly/" if r["track"] == "anomaly" else ""
    if r["annotation_kind"] == "classification_only":
        prefix = "classification_only/"
    outputs = []
    for copy in range(r["augmentations"] + 1):
        im, bb, cc, mm = image, boxes, r["classes"], mask
        copy_seed = int(digest(f"{seed}:{r['id']}:{copy}".encode())[:8], 16)
        if copy:
            im, bb, cc, mm = augment(image, boxes, r["classes"], mask, copy_seed)
        stem = r["id"] + (f"_aug{copy}" if copy else "")
        image_rel = prefix + f"images/{r['split']}/{stem}.jpg"
        label_rel = prefix + f"labels/{r['split']}/{stem}.txt"
        save_image(out / image_rel, im)
        (out / label_rel).write_text(to_yolo(bb, cc), encoding="utf-8")
        mask_rel = None
        if mm is not None:
            mask_rel = prefix + f"masks/{r['split']}/{stem}.png"
            save_image(out / mask_rel, mm, mask=True)
        outputs.append(
            {
                "image": image_rel,
                "label": label_rel,
                "mask": mask_rel,
                "parent_id": r["id"],
                "source": r["source"],
                "split": r["split"],
                "track": r["track"],
                "raw": r["raw"],
                "raw_label": r["raw_label"],
                "pixel_sha256": r["pixel_sha256"],
                "class_name": r["class_name"],
                "annotation_kind": r["annotation_kind"],
                "augmented": bool(copy),
                "augmentation_seed": copy_seed if copy else None,
                "classes": cc,
                "box_count": len(bb),
                "transform": transform,
                "native_split": r["native_split"],
            }
        )
    return outputs


def write_json(path: Path, value: Any) -> None:
    """Write readable build metadata."""
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def tile_windows(width: int, height: int) -> list[list[int]]:
    """Cover a native-height AITEX strip, including its non-stride-aligned end."""
    size, stride = AITEX_TILING["size"], AITEX_TILING["stride"]
    if height != size or width < size:
        raise ValueError(f"Expected AITEX strip height {size}, got {width}x{height}")
    starts = sorted(set(range(0, width - size + 1, stride)) | {width - size})
    return [[x, 0, x + size, size] for x in starts]


def plan_aitex_tiles(records: list[dict], seed: int) -> dict:
    """Retain all positive crops; deterministically cap negatives per split.

    Splits and training augmentation quotas already belong to the source strip.
    Round-robin sampling across source strips avoids concentrating backgrounds.
    Unknown-localization positives never supply crops or background candidates.
    """
    candidates = defaultdict(lambda: defaultdict(list))
    counts = {s: Counter() for s in SPLITS}
    for r in records:
        if r["source"] != "aitex" or r["annotation_kind"] == "classification_only":
            continue
        w, h = r["original_wh"]
        mask = load_mask(r["masks"], (h, w))
        kept = []
        for window in tile_windows(w, h):
            x1, y1, x2, y2 = window
            boxes = mask_boxes(mask[y1:y2, x1:x2])
            tile = {
                "window": window,
                "boxes": boxes,
                "id": f"{r['id']}_tile{x1:04d}_{y1:04d}",
            }
            counts[r["split"]]["candidate_tiles"] += 1
            if boxes:
                kept.append(tile)
                counts[r["split"]]["positive_tiles"] += 1
            else:
                candidates[r["split"]][r["id"]].append(tile)
                counts[r["split"]]["background_candidates"] += 1
        r["aitex_tiles"] = kept
    by_id = {r["id"]: r for r in records}
    for split in SPLITS:
        groups = candidates[split]
        budget = math.floor(
            counts[split]["positive_tiles"] * AITEX_TILING["backgrounds_per_positive"]
        )
        keys = sorted(groups, key=lambda k: digest(f"{seed}:{split}:{k}".encode()))
        for key in keys:
            groups[key].sort(key=lambda t: digest(f"{seed}:{t['id']}".encode()))
        selected = 0
        while selected < budget and any(groups.values()):
            for key in keys:
                if selected >= budget:
                    break
                if groups[key]:
                    by_id[key]["aitex_tiles"].append(groups[key].pop())
                    selected += 1
        counts[split]["sampled_backgrounds"] = selected
        counts[split]["discarded_backgrounds"] = (
            counts[split]["background_candidates"] - selected
        )
    for r in records:
        if "aitex_tiles" in r:
            r["aitex_tiles"].sort(key=lambda t: t["window"])
    return {
        "policy": AITEX_TILING,
        "splits": counts,
        "source_strips_without_selected_tiles": sum(
            "aitex_tiles" in r and not r["aitex_tiles"] for r in records
        ),
    }


def augment_aitex(
    image: np.ndarray, boxes: list, classes: list, mask: np.ndarray, seed: int
) -> tuple:
    """Keep tile-edge positives: omit rotation if it removes a labeled region."""
    try:
        result = augment(image, boxes, classes, mask, seed)
    except ValueError as error:
        if str(error) != "Augmentation removed every defect box":
            raise
        result = None
    if (
        result is not None
        and len(result[1]) == len(boxes)
        and all(
            result[3][
                max(0, math.floor(y1)) : min(640, math.ceil(y2)),
                max(0, math.floor(x1)) : min(640, math.ceil(x2)),
            ].any()
            for x1, y1, x2, y2 in result[1]
        )
    ):
        return (*result, "standard")
    fallback = A.Compose(
        [
            A.HorizontalFlip(p=0.5),
            A.RandomBrightnessContrast(
                brightness_limit=0.12, contrast_limit=0.12, p=0.8
            ),
        ],
        bbox_params=A.BboxParams(
            format="pascal_voc", label_fields=["classes"], clip=True
        ),
        seed=seed,
    )
    r = fallback(image=image, bboxes=boxes, classes=classes, mask=mask)
    return (
        r["image"],
        list(r["bboxes"]),
        [int(c) for c in r["classes"]],
        r["mask"],
        "no_rotation_boundary_fallback",
    )


def convert_aitex_tiles(r: dict, out: Path, seed: int) -> list[dict]:
    """Crop native pixels/masks, then transform local boxes and train copies."""
    if "aitex_tiles" not in r:
        raise ValueError("AITEX tile selection must run before conversion")
    image = load_rgb(Path(r["path"]))
    mask = load_mask(r["masks"], image.shape[:2])
    rows = []
    for tile in r["aitex_tiles"]:
        x1, y1, x2, y2 = tile["window"]
        positive = bool(tile["boxes"])
        local_mask = mask[y1:y2, x1:x2] if positive else None
        im, boxes, mm, transform = letterbox(
            image[y1:y2, x1:x2], tile["boxes"], local_mask
        )
        classes = [NAMES.index(r["class_name"])] * len(boxes) if positive else []
        copies = r["augmentations"] if positive and r["split"] == "train" else 0
        for copy in range(copies + 1):
            copy_seed = int(digest(f"{seed}:{tile['id']}:{copy}".encode())[:8], 16)
            pixels, bb, cc, mask_out = im, boxes, classes, mm
            augmentation_policy = None
            if copy:
                pixels, bb, cc, mask_out, augmentation_policy = augment_aitex(
                    im, boxes, classes, mm, copy_seed
                )
            stem = tile["id"] + (f"_aug{copy}" if copy else "")
            image_rel = f"images/{r['split']}/{stem}.jpg"
            label_rel = f"labels/{r['split']}/{stem}.txt"
            save_image(out / image_rel, pixels)
            (out / label_rel).write_text(to_yolo(bb, cc), encoding="utf-8")
            mask_rel = None
            if mask_out is not None:
                mask_rel = f"masks/{r['split']}/{stem}.png"
                save_image(out / mask_rel, mask_out, mask=True)
            rows.append(
                {
                    "image": image_rel,
                    "label": label_rel,
                    "mask": mask_rel,
                    "parent_id": r["id"],
                    "tile_id": tile["id"],
                    "tile_window": tile["window"],
                    "source": "aitex",
                    "split": r["split"],
                    "track": r["track"],
                    "raw": r["raw"],
                    "raw_label": r["raw_label"],
                    "pixel_sha256": r["pixel_sha256"],
                    "source_class_name": r["class_name"],
                    "class_name": r["class_name"] if positive else "normal",
                    "annotation_kind": "mask" if positive else "normal",
                    "augmented": bool(copy),
                    "augmentation_seed": copy_seed if copy else None,
                    "augmentation_policy": augmentation_policy,
                    "classes": cc,
                    "box_count": len(bb),
                    "transform": transform,
                    "native_split": r["native_split"],
                }
            )
    return rows


def verify_aitex_tiles(sources: list[dict], rows: list[dict], out: Path) -> None:
    """Check tile coverage, source coordinates and saved unaugmented geometry."""
    originals = {
        r.get("tile_id"): r for r in rows if not r["augmented"] and r.get("tile_id")
    }
    for split in SPLITS:
        tiles = [r for r in originals.values() if r["split"] == split]
        positives = sum(bool(r["classes"]) for r in tiles)
        if len(tiles) - positives > math.floor(positives * 0.25):
            raise ValueError("AITEX background budget exceeded")
    if any(r.get("tile_id") and not r["classes"] and r["augmented"] for r in rows):
        raise ValueError("AITEX background tiles must not be augmented")
    for source in sources:
        if "aitex_tiles" not in source:
            continue
        w, h = source["original_wh"]
        mask = load_mask(source["masks"], (h, w))
        cover = np.zeros_like(mask)
        for tile in source["aitex_tiles"]:
            x1, y1, x2, y2 = tile["window"]
            crop = mask[y1:y2, x1:x2]
            boxes = mask_boxes(crop)
            if boxes != tile["boxes"]:
                raise ValueError("Tile boxes disagree with raw mask crop")
            row = originals[tile["id"]]
            if (
                row["parent_id"] != source["id"]
                or row["split"] != source["split"]
                or row["tile_window"] != tile["window"]
            ):
                raise ValueError("Tile provenance mismatch")
            # Independent 256->640 translation/scale, not the converter's helper.
            expected = np.asarray(boxes, dtype=float).reshape(-1, 4) * 2.5
            actual, _ = read_yolo(out / row["label"], 640, 640)
            np.testing.assert_allclose(
                np.asarray(actual).reshape(-1, 4), expected, atol=1e-5
            )
            if boxes:
                cover[y1:y2, x1:x2] |= crop
                saved = load_mask([str(out / row["mask"])], (640, 640))
                np.testing.assert_array_equal(
                    saved, cv2.resize(crop, (640, 640), interpolation=cv2.INTER_NEAREST)
                )
            elif row["class_name"] != "normal" or row["mask"]:
                raise ValueError("Background tile mislabeled")
        if not np.array_equal(mask, cover):
            raise ValueError(f"AITEX foreground omitted: {source['raw']}")


def require_real_only_output(out: Path) -> None:
    """Prevent a base rebuild from silently orphaning synthetic derivatives."""
    if (out / "synthetic-config.json").exists():
        raise ValueError(
            "Synthetic layer exists. Rebuild the real base into a fresh --output "
            "directory, then regenerate synthetic examples against that base."
        )


def build(
    raw: Path, out: Path, seed: int = 42, workers: int = 8, resume: bool = False
) -> None:
    """Audit, split, transform and emit data; existing unrelated output is refused."""
    cv2.setNumThreads(1)
    raw, out = raw.resolve(), out.resolve()
    require_real_only_output(out)
    if raw == out or raw in out.parents or out in raw.parents:
        raise ValueError("Raw/output paths must be disjoint")
    marker = out / "build-config.json"
    config = {
        "schema": 1,
        "raw": str(raw),
        "seed": seed,
        "size": 640,
        "names": NAMES,
        "aitex_tiling": AITEX_TILING,
    }
    if (
        out.exists()
        and any(out.iterdir())
        and (
            not resume
            or not marker.is_file()
            or json.loads(marker.read_text()) != config
        )
    ):
        raise ValueError(
            "Output is nonempty. Only --resume with matching build-config is allowed."
        )
    records = scan_sources(raw)
    print(f"Decoding and hashing {len(records)} originals before splitting", flush=True)
    inspected = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for i, r in enumerate(pool.map(inspect_record, records), 1):
            inspected.append(r)
            if i % 5000 == 0:
                print(f"Audited {i}/{len(records)}", flush=True)
    records = inspected
    leakage = assign_splits(records, seed)
    # Image-level class frequencies, exclusively training data, determine copies.
    frequency = Counter(
        c
        for r in records
        if r["track"] == "multiclass" and r["split"] == "train"
        for c in set(r["classes"])
    )
    target = max(frequency.values(), default=1)
    for r in records:
        r["augmentations"] = 0
        if r["split"] == "train" and r["annotation_kind"] != "classification_only":
            if r["track"] == "anomaly":
                # Normal autoencoder examples only; retain all original binary data.
                r["augmentations"] = 1 if r["class_name"] == "normal" else 0
            else:
                r["augmentations"] = max(
                    [
                        min(3, math.ceil(target / frequency[c]))
                        for c in set(r["classes"])
                    ]
                    or [1]
                )
    tiling = plan_aitex_tiles(records, seed)
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "aitex-tiling.json", tiling)
    write_json(marker, config)
    for prefix in ("", "anomaly", "classification_only"):
        for kind in ("images", "labels", "masks"):
            for split in SPLITS:
                (out / prefix / kind / split).mkdir(parents=True, exist_ok=True)
    with (out / "source-manifest.jsonl").open("w", encoding="utf-8") as file:
        for r in records:
            file.write(json.dumps(r) + "\n")
    write_json(
        out / "audit.json",
        {
            "sources": {
                s: dict(Counter(r["class_name"] for r in records if r["source"] == s))
                for s in SOURCES
            },
            "input_images": len(records),
            "leakage": leakage,
            "training_class_frequency": dict(frequency),
            "raw_dimensions": dict(Counter(str(r["original_wh"]) for r in records)),
        },
    )
    print("Input audit saved; conversion begins", flush=True)
    with (
        (out / "manifest.jsonl").open("w", encoding="utf-8") as file,
        ThreadPoolExecutor(max_workers=workers) as pool,
    ):
        for i, rows in enumerate(
            pool.map(lambda r: convert_record(r, out, seed), records), 1
        ):
            for row in rows:
                file.write(json.dumps(row) + "\n")
            if i % 2500 == 0:
                print(f"Converted {i}/{len(records)} source images", flush=True)
    for prefix, names in (("", NAMES), ("anomaly", ["defective"])):
        yaml_data = {
            "path": (out / prefix).as_posix(),
            "train": "images/train",
            "val": "images/val",
            "test": "images/test",
            "names": dict(enumerate(names)),
            "nc": len(names),
        }
        (out / prefix / "data.yaml").write_text(
            yaml.safe_dump(yaml_data, sort_keys=False), encoding="utf-8"
        )
    print("Conversion complete; run --verify for independent output checks", flush=True)


def verify_row(row: dict, out: Path) -> dict:
    """Independently decode saved images, labels and masks; check saved geometry."""
    image = load_rgb(out / row["image"])
    if image.shape != (640, 640, 3):
        raise ValueError(f"Wrong output shape: {row['image']}")
    boxes, classes = read_yolo(out / row["label"], 640, 640)
    limit = 1 if row["track"] == "anomaly" else len(NAMES)
    if (
        any(c >= limit for c in classes)
        or classes != row["classes"]
        or len(boxes) != row["box_count"]
    ):
        raise ValueError(f"Output class/count mismatch: {row['label']}")
    if row["augmented"] and row["split"] != "train":
        raise ValueError("Augmentation leaked into held-out split")
    if row["source"] == "zju_leaper" and row["track"] != "anomaly":
        raise ValueError("ZJU leaked into multiclass data")
    if row["class_name"] == "normal" and boxes:
        raise ValueError("Normal sample has defect boxes")
    tiny = sum(min(x2 - x1, y2 - y1) < 1 for x1, y1, x2, y2 in boxes)
    vanished = 0
    if row["mask"]:
        mask = load_mask([str(out / row["mask"])], (640, 640))
        vanished = int(not mask.any())
        if vanished:
            raise ValueError(
                f"Positive mask erased during preprocessing: {row['mask']}"
            )
        # Inclusive rasterization tolerates subpixel rounding/resampling, not shifts.
        if row["annotation_kind"] in ("mask", "yolo", "synthetic_mask") and mask.any():
            cover = np.zeros((640, 640), dtype=np.uint8)
            for x1, y1, x2, y2 in boxes:
                cv2.rectangle(
                    cover,
                    (max(0, math.floor(x1) - 1), max(0, math.floor(y1) - 1)),
                    (min(639, math.ceil(x2) + 1), min(639, math.ceil(y2) + 1)),
                    1,
                    -1,
                )
            missed = int(((mask > 0) & (cover == 0)).sum())
            if missed:
                raise ValueError(f"{missed} mask pixels outside boxes: {row['image']}")
    return {"tiny_boxes": tiny, "empty_resized_masks": vanished}


def sanity_images(rows: list[dict], out: Path, seed: int) -> None:
    """Draw five actual saved originals per source for human visual review."""
    target = out / "_sanity_check"
    target.mkdir(exist_ok=True)
    for source in SOURCES:
        candidates = [
            r
            for r in rows
            if r["source"] == source and not r["augmented"] and r["classes"]
        ]
        chosen = random.Random(f"sanity:{seed}:{source}").sample(
            candidates, min(5, len(candidates))
        )
        panels = []
        for i, r in enumerate(chosen):
            image = load_rgb(out / r["image"])
            boxes, classes = read_yolo(out / r["label"], 640, 640)
            for box, c in zip(boxes, classes):
                x1, y1, x2, y2 = map(round, box)
                cv2.rectangle(
                    image, (x1, y1), (min(639, x2), min(639, y2)), (255, 40, 40), 2
                )
                label = "defective" if r["track"] == "anomaly" else NAMES[c]
                cv2.putText(
                    image,
                    label,
                    (max(0, x1), max(14, y1 - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 40, 40),
                    1,
                )
            cv2.putText(
                image,
                source + " " + r["annotation_kind"],
                (5, 625),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 0),
                1,
            )
            save_image(target / f"{source}_{i+1}.jpg", image)
            # Fixed-size detail crop avoids hiding narrow-strip defects in a sheet.
            largest = max(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
            cx, cy = (largest[0] + largest[2]) / 2, (largest[1] + largest[3]) / 2
            left = max(0, min(512, round(cx) - 64))
            top = max(0, min(512, round(cy) - 64))
            detail = cv2.resize(image[top : top + 128, left : left + 128], (320, 320))
            panels.append(
                np.concatenate([cv2.resize(image, (320, 320)), detail], axis=0)
            )
        save_image(target / f"{source}_contact.jpg", np.concatenate(panels, axis=1))
        write_json(target / f"{source}.json", chosen)


def verify(out: Path, workers: int = 8) -> dict:
    """Verify all output files, splitting, distributions and useful track manifests."""
    cv2.setNumThreads(1)
    rows = [
        json.loads(line) for line in (out / "manifest.jsonl").read_text().splitlines()
    ]
    original_inputs = [
        json.loads(line)
        for line in (out / "source-manifest.jsonl").read_text().splitlines()
    ]
    if any(r.get("synthetic", False) for r in rows):
        from synthetic_defects import verify_synthetic_rows

        verify_synthetic_rows(rows, out)
    actual_originals = Counter(
        r.get("tile_id", r["parent_id"]) for r in rows if not r["augmented"]
    )
    expected_originals = Counter(
        identity
        for r in original_inputs
        for identity in (
            [t["id"] for t in r["aitex_tiles"]] if "aitex_tiles" in r else [r["id"]]
        )
    )
    if actual_originals != expected_originals:
        raise ValueError("Original source samples were omitted or duplicated in output")
    verify_aitex_tiles(original_inputs, rows, out)
    parents, hashes = {}, {}
    counts: dict[str, Counter] = defaultdict(Counter)
    boxes: dict[str, Counter] = defaultdict(Counter)
    source_counts: dict[str, Counter] = defaultdict(Counter)
    image_class_counts: dict[str, Counter] = defaultdict(Counter)
    expected_files = set()
    for r in rows:
        for identity, mapping in (
            (r["parent_id"], parents),
            (r["pixel_sha256"], hashes),
        ):
            previous = mapping.setdefault(identity, r["split"])
            if previous != r["split"]:
                raise ValueError(f"Cross-split leakage: {r['raw']}")
        key = (
            (
                "classification_only"
                if r["annotation_kind"] == "classification_only"
                else r["track"]
            )
            + "/"
            + r["split"]
        )
        counts[key]["images"] += 1
        counts[key]["augmented" if r["augmented"] else "originals"] += 1
        if r.get("synthetic", False):
            counts[key]["synthetic"] += 1
        counts[key]["positive" if r["classes"] else "empty_labels"] += 1
        for c in r["classes"]:
            boxes[key]["defective" if r["track"] == "anomaly" else NAMES[c]] += 1
        source_counts[key][r["source"]] += 1
        image_class_counts[key][r["class_name"]] += 1
        for field in ("image", "label", "mask"):
            if r[field]:
                if r[field] in expected_files:
                    raise ValueError(f"Duplicate output path: {r[field]}")
                expected_files.add(r[field])
    actual = {
        p.relative_to(out).as_posix()
        for prefix in ("", "anomaly", "classification_only")
        for kind in ("images", "labels", "masks")
        for p in (out / prefix / kind).rglob("*")
        if p.is_file() and p.suffix != ".cache"
    }
    if actual != expected_files:
        raise ValueError(
            f"Output files differ: missing={list(expected_files-actual)[:5]}, extra={list(actual-expected_files)[:5]}"
        )
    for track in ("multiclass", "anomaly"):
        for split in SPLITS:
            if not counts[track + "/" + split]["positive"]:
                raise ValueError(f"Empty positive split: {track}/{split}")
    metrics = Counter()
    source_geometry = defaultdict(Counter)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for i, result in enumerate(pool.map(lambda r: verify_row(r, out), rows), 1):
            metrics.update(result)
            source_geometry[rows[i - 1]["source"]].update(result)
            if i % 10000 == 0:
                print(f"Verified {i}/{len(rows)} output images", flush=True)
    for split in SPLITS:
        normal = [
            r["image"]
            for r in rows
            if r["track"] == "anomaly"
            and r["split"] == split
            and r["class_name"] == "normal"
        ]
        (out / "anomaly" / f"normal_{split}.txt").write_text(
            "".join("./" + p.removeprefix("anomaly/") + "\n" for p in normal),
            encoding="utf-8",
        )
        strong = [
            r["image"]
            for r in rows
            if r["track"] == "multiclass"
            and r["split"] == split
            and not r.get("synthetic", False)
            and r["annotation_kind"] not in ("weak_full_image", "classification_only")
        ]
        (out / f"strong_{split}.txt").write_text(
            "".join("./" + p + "\n" for p in strong), encoding="utf-8"
        )
        with (out / f"classification_{split}.jsonl").open(
            "w", encoding="utf-8"
        ) as file:
            for r in rows:
                if r["track"] == "multiclass" and r["split"] == split:
                    file.write(json.dumps(r) + "\n")
    config = json.loads((out / "build-config.json").read_text())
    sanity_images(rows, out, config["seed"])
    report = {
        "output_images": len(rows),
        "counts": counts,
        "box_counts": boxes,
        "source_counts": source_counts,
        "image_class_counts": image_class_counts,
        "tilda_repairs": dict(
            sum(
                (
                    Counter(r.get("tilda_mask_reconciliation", {}))
                    for r in original_inputs
                ),
                Counter(),
            )
        ),
        "classification_only_sources": [
            r["raw"]
            for r in original_inputs
            if r["annotation_kind"] == "classification_only"
        ],
        "geometry_metrics": metrics,
        "geometry_by_source": source_geometry,
        "aitex_image_class_counts": {
            split: dict(
                Counter(
                    r["class_name"]
                    for r in rows
                    if r["source"] == "aitex"
                    and r["split"] == split
                    and r.get("tile_id")
                )
            )
            for split in SPLITS
        },
        "cross_split_parent_overlap": 0,
        "cross_split_pixel_overlap": 0,
        "source_images": len(original_inputs),
        "seed": config["seed"],
        "manifest_sha256": digest((out / "manifest.jsonl").read_bytes()),
        "source_manifest_sha256": digest((out / "source-manifest.jsonl").read_bytes()),
        "python": platform.python_version(),
        "packages": {
            name: version(name)
            for name in (
                "albumentations",
                "opencv-python-headless",
                "numpy",
                "pillow",
                "ultralytics-opencv-headless",
                "torch",
                "PyYAML",
            )
        },
        "verification": "all output images decoded; labels, masks, file pairs and split isolation passed",
    }
    write_json(out / "verification.json", report)
    print(json.dumps(report, indent=2), flush=True)
    return report


def rebuild_aitex(out: Path) -> None:
    """Stage/validate AITEX only, archive its old files, preserve other sources.

    Existing source splits and augmentation quotas are reused. Retired generated
    strips remain recoverable under the ignored rebuild directory; raw files and
    all other sources' image/label/mask outputs are never written here.
    """
    cv2.setNumThreads(1)
    out = out.resolve()
    require_real_only_output(out)
    source_path, manifest_path = out / "source-manifest.jsonl", out / "manifest.jsonl"
    sources = [json.loads(line) for line in source_path.read_text().splitlines()]
    rows = [json.loads(line) for line in manifest_path.read_text().splitlines()]
    config = json.loads((out / "build-config.json").read_text())
    other_rows = [r for r in rows if r["source"] != "aitex"]

    def safe_path(relative: str, root: Path, aitex_only: bool = False) -> Path:
        path = (root / relative).resolve()
        if root not in path.parents or (
            aitex_only and not path.name.startswith("aitex_")
        ):
            raise ValueError(f"Unsafe generated output path: {path}")
        return path

    def other_snapshot() -> str:
        fingerprint = hashlib.sha256(json.dumps(other_rows).encode())
        for row in other_rows:
            for field in ("image", "label", "mask"):
                if row[field]:
                    path = safe_path(row[field], out)
                    stat = path.stat()
                    fingerprint.update(
                        f"{row[field]}:{stat.st_size}:{stat.st_mtime_ns}\n".encode()
                    )
        return fingerprint.hexdigest()

    print(
        "Snapshotting other four sources' manifest, sizes and modification times",
        flush=True,
    )
    before = other_snapshot()
    for i, old in enumerate(sources):
        if old["source"] != "aitex":
            continue
        new = inspect_record(old)
        for key in ("raw_sha256", "pixel_sha256", "annotation_sha256"):
            if new[key] != old[key]:
                raise ValueError(f"AITEX input changed since audit: {old['raw']}")
        sources[i] = new
    tiling = plan_aitex_tiles(sources, config["seed"])
    print(json.dumps(tiling, indent=2), flush=True)
    workspace = Path(tempfile.mkdtemp(prefix="_aitex_rebuild_", dir=out))
    stage, archive = workspace / "stage", workspace / "previous"
    for prefix in ("", "classification_only"):
        for kind in ("images", "labels", "masks"):
            for split in SPLITS:
                (stage / prefix / kind / split).mkdir(parents=True, exist_ok=True)
    generated = []
    for source in sources:
        if source["source"] == "aitex":
            generated.extend(convert_record(source, stage, config["seed"]))
    for row in generated:
        verify_row(row, stage)
    verify_aitex_tiles(sources, generated, stage)
    print(f"Staged and validated {len(generated)} AITEX outputs", flush=True)
    old_paths = {
        r[f]
        for r in rows
        if r["source"] == "aitex"
        for f in ("image", "label", "mask")
        if r[f]
    }
    new_paths = {r[f] for r in generated for f in ("image", "label", "mask") if r[f]}
    # Resolve every exact source/destination before moving any generated file.
    old_moves = [
        (safe_path(p, out, True), safe_path(p, archive, True))
        for p in sorted(old_paths)
    ]
    new_moves = [
        (safe_path(p, stage, True), safe_path(p, out, True)) for p in sorted(new_paths)
    ]
    for _, destination in new_moves:
        if (
            destination.exists()
            and destination.relative_to(out).as_posix() not in old_paths
        ):
            raise ValueError(f"Refuse overwriting unrelated output: {destination}")
    archive.mkdir(parents=True, exist_ok=True)
    for name in (
        "manifest.jsonl",
        "source-manifest.jsonl",
        "build-config.json",
        "verification.json",
        "aitex-tiling.json",
        "ultralytics-verification.json",
    ):
        if (out / name).is_file():
            shutil.copy2(out / name, archive / name)
    for source, destination in old_moves + new_moves:
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.rename(destination)
    replaced = []
    inserted = False
    for row in rows:
        if row["source"] == "aitex":
            if not inserted:
                replaced.extend(generated)
                inserted = True
        else:
            replaced.append(row)
    if not inserted:
        raise ValueError("Existing manifest had no AITEX records")
    for path, records in ((source_path, sources), (manifest_path, replaced)):
        with path.open("w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record) + "\n")
    config["aitex_tiling"] = AITEX_TILING
    write_json(out / "build-config.json", config)
    after = other_snapshot()
    if before != after or [r for r in replaced if r["source"] != "aitex"] != other_rows:
        raise ValueError("Non-AITEX output snapshot changed")
    tiling.update(
        {
            "output_images": len(generated),
            "previous_output_images": len(rows) - len(other_rows),
            "unchanged_other_source_images": len(other_rows),
            "other_source_manifest_and_file_stat_sha256": after,
            "archive": archive.relative_to(out).as_posix(),
        }
    )
    write_json(out / "aitex-tiling.json", tiling)
    print(
        f"AITEX replaced; previous outputs archived at {archive}. Run --verify.",
        flush=True,
    )


def refresh_semantic(out: Path) -> None:
    """Rebuild semantic outputs after annotation repair, preserving split IDs.

    Used during this build's verification loop. A fresh build already applies
    the same repair. Refuse changed source pixels or changed copy counts.
    """
    require_real_only_output(out)
    source_path = out / "source-manifest.jsonl"
    sources = [json.loads(line) for line in source_path.read_text().splitlines()]
    config = json.loads((out / "build-config.json").read_text())
    replacements = {}
    for i, old in enumerate(sources):
        if old["track"] != "multiclass":
            continue
        new = inspect_record(old)
        if old["pixel_sha256"] != new["pixel_sha256"]:
            raise ValueError(f"Raw image changed since split: {old['raw']}")
        sources[i] = new
        replacements[old["id"]] = convert_record(new, out, config["seed"])
    rows = [
        json.loads(line) for line in (out / "manifest.jsonl").read_text().splitlines()
    ]
    replaced = []
    seen = set()
    for row in rows:
        parent = row["parent_id"]
        if parent in replacements:
            if parent not in seen:
                replaced.extend(replacements[parent])
                seen.add(parent)
        else:
            replaced.append(row)
    if len(replaced) != len(rows):
        raise ValueError("Refresh changed image count")
    for path, records in ((source_path, sources), (out / "manifest.jsonl", replaced)):
        with path.open("w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record) + "\n")
    print(
        f"Refreshed {len(replacements)} semantic originals and their train augmentations",
        flush=True,
    )


def main() -> None:
    """CLI entry point; verification can rerun independently of conversion."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=ROOT / "raw")
    parser.add_argument("--output", type=Path, default=ROOT / "processed")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--refresh-semantic", action="store_true")
    parser.add_argument("--rebuild-aitex", action="store_true")
    args = parser.parse_args()
    if args.rebuild_aitex:
        rebuild_aitex(args.output.resolve())
    elif args.refresh_semantic:
        refresh_semantic(args.output.resolve())
    elif args.verify:
        verify(args.output.resolve(), args.workers)
    else:
        build(args.raw, args.output, args.seed, args.workers, args.resume)


if __name__ == "__main__":
    main()
