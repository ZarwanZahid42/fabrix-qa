"""Disclosed, seeded procedural training defects; never synthesize held-out data.

These are appearance proxies, not simulated textile physics or new real labels.
Original ZJU binary data stays unchanged; only tagged derivatives enter detection.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np
from build_dataset import NAMES, ROOT, load_rgb, read_yolo, to_yolo, verify_row

CLASSES = ("crease", "edge_damage", "foreign_object")
VERSION = "procedural-fabric-v1"


def sha(data: bytes) -> str:
    """Hash source bytes, recipe identities and audit snapshots."""
    return hashlib.sha256(data).hexdigest()


def curve(points: np.ndarray) -> np.ndarray:
    """Sample a quadratic Bezier curve into integer image coordinates."""
    t = np.linspace(0, 1, 160)[:, None]
    return np.rint(
        (1 - t) ** 2 * points[0] + 2 * (1 - t) * t * points[1] + t**2 * points[2]
    ).astype(np.int32)


def render_defect(
    background: np.ndarray, kind: str, seed: int
) -> tuple[np.ndarray, np.ndarray, list, dict]:
    """Render a proxy and derive an exact box from pixels actually changed.

    Lossless PNG preserves the unmodified background outside the support mask.
    No text or watermark is placed in training pixels; disclosure is metadata.
    """
    if background.shape != (640, 640, 3) or background.dtype != np.uint8:
        raise ValueError("Expected uint8 RGB 640x640 background")
    if kind not in CLASSES:
        raise ValueError(f"Unsupported synthetic class: {kind}")
    rng = np.random.default_rng(seed)
    base = background.astype(np.float32)
    layer = np.zeros((640, 640), np.uint8)
    params = {}
    if kind == "crease":
        center = rng.uniform(200, 440, 2)
        angle = rng.uniform(0, 2 * math.pi)
        direction = np.array([math.cos(angle), math.sin(angle)])
        normal = np.array([-direction[1], direction[0]])
        length = rng.uniform(150, 350)
        points = np.array(
            [
                center - direction * length / 2,
                center + normal * rng.uniform(-65, 65),
                center + direction * length / 2,
            ]
        )
        thickness = int(rng.integers(1, 4))
        cv2.polylines(layer, [curve(points)], False, 255, thickness, cv2.LINE_AA)
        core = layer.astype(np.float32) / 255
        shadow = cv2.GaussianBlur(core, (31, 31), 4)
        alpha = np.clip(core * rng.uniform(0.25, 0.5) + shadow * 0.9, 0, 0.7)
        result = base * (1 - alpha[..., None])
        # Adjacent soft ridge light suggests a fold, rather than only a scratch.
        ridge = np.zeros_like(layer)
        cv2.polylines(
            ridge, [curve(points + normal * 3)], False, 255, thickness, cv2.LINE_AA
        )
        light = cv2.GaussianBlur(ridge.astype(np.float32) / 255, (13, 13), 2) * 0.25
        result += (255 - result) * light[..., None]
        params = {
            "style": "curved_fold_shadow_and_ridge",
            "points": points.tolist(),
            "thickness": thickness,
        }
    elif kind == "edge_damage":
        start = int(rng.integers(80, 400))
        length = int(rng.integers(100, 230))
        xs = np.arange(start, min(620, start + length), 5)
        depth = rng.integers(8, 36, len(xs))
        polygon = np.array(
            [[int(xs[0]), 0], *zip(xs.tolist(), depth.tolist()), [int(xs[-1]), 0]],
            np.int32,
        )
        cv2.fillPoly(layer, [polygon], 255)
        # Ragged cutaway with projecting fibers; randomize all four image edges.
        dark = rng.uniform(5, 35)
        local_mean = float(base[:40, start : start + length].mean())
        void = dark if local_mean > 60 else rng.uniform(150, 190)
        top = base.copy()
        top[layer > 0] = void + rng.uniform(-4, 4, (int((layer > 0).sum()), 1))
        for x, y in zip(xs[::2], depth[::2]):
            end = (int(x + rng.integers(-8, 9)), max(0, int(y - rng.integers(5, 20))))
            color = tuple(float(v) for v in base[int(y), int(x)])
            cv2.line(top, (int(x), int(y)), end, color, 1, cv2.LINE_AA)
        # Rotate the changed overlay, not the underlying source fabric.
        changed = np.any(top != base, axis=2)
        rotation = int(rng.integers(0, 4))
        rotated_mask = np.rot90(changed, rotation)
        rotated_overlay = np.rot90(top, rotation)
        result = base.copy()
        result[rotated_mask] = rotated_overlay[rotated_mask]
        params = {
            "style": "border_cutaway_with_frayed_fibers",
            "quarter_turns": rotation,
            "start": start,
            "length": length,
        }
    else:
        cx, cy = rng.integers(90, 550, 2)
        if rng.random() < 0.45:
            points = np.array(
                [
                    [cx - 25, cy - 10],
                    [cx + rng.integers(-20, 21), cy + 25],
                    [cx + 30, cy - 5],
                ]
            )
            cv2.polylines(
                layer, [curve(points)], False, 255, int(rng.integers(2, 6)), cv2.LINE_AA
            )
            style = "stray_thread"
        else:
            theta = np.linspace(0, 2 * math.pi, 12, endpoint=False)
            radius = rng.uniform(0.6, 1.2, 12)
            points = np.stack(
                [
                    cx + np.cos(theta) * radius * rng.uniform(9, 24),
                    cy + np.sin(theta) * radius * rng.uniform(8, 19),
                ],
                axis=1,
            )
            cv2.fillPoly(layer, [points.astype(np.int32)], 255, cv2.LINE_AA)
            style = "irregular_debris"
        local_mean = float(base[cy - 35 : cy + 35, cx - 35 : cx + 35].mean())
        shade = rng.uniform(15, 50) if local_mean >= 110 else rng.uniform(195, 235)
        tint = rng.uniform(-8, 8, 3)
        alpha = layer.astype(np.float32) / 255 * rng.uniform(0.75, 0.95)
        texture = rng.normal(0, 3, (640, 640, 1))
        result = (
            base * (1 - alpha[..., None]) + (shade + tint + texture) * alpha[..., None]
        )
        params = {"style": style, "center": [int(cx), int(cy)], "shade": float(shade)}
    result = np.clip(np.rint(result), 0, 255).astype(np.uint8)
    mask = np.any(result != background, axis=2).astype(np.uint8)
    yy, xx = np.where(mask)
    if len(xx) < 8:
        raise ValueError("Synthetic defect is not visibly supported by enough pixels")
    box = [float(xx.min()), float(yy.min()), float(xx.max() + 1), float(yy.max() + 1)]
    return result, mask, box, params


def eligible_backgrounds(rows: list[dict], source: str) -> list[dict]:
    """Use unique, original train normals; reject any held-out parent/hash."""
    held_parents = {r["parent_id"] for r in rows if r["split"] != "train"}
    held_hashes = {r["pixel_sha256"] for r in rows if r["split"] != "train"}
    chosen = {}
    for row in sorted(rows, key=lambda r: r["image"]):
        if (
            row.get("synthetic", False)
            or row["split"] != "train"
            or row["augmented"]
            or row["class_name"] != "normal"
            or row["classes"]
            or row["mask"]
            or (source != "all" and row["source"] != source)
        ):
            continue
        transform = row["transform"]
        if transform["pad_lt"] != [0, 0] or transform["resized_wh"] != [640, 640]:
            continue  # Do not mistake padding for a real fabric border.
        if row["parent_id"] in held_parents or row["pixel_sha256"] in held_hashes:
            raise ValueError("Background lineage also appears in a held-out split")
        chosen.setdefault(row["pixel_sha256"], row)
    if not chosen:
        raise ValueError("No eligible original train-only fabric backgrounds")
    return list(chosen.values())


def background_plan(
    rows: list[dict], counts: dict[str, int], seed: int, source: str
) -> list[tuple]:
    """Disjoint hash partitions give stable, distinct parents as quotas grow."""
    candidates = eligible_backgrounds(rows, source)
    plan = []
    for index, kind in enumerate(CLASSES):
        pool = [r for r in candidates if int(r["pixel_sha256"][:8], 16) % 3 == index]
        pool.sort(key=lambda r: sha(f"{seed}:{kind}:{r['pixel_sha256']}".encode()))
        if counts[kind] > len(pool):
            raise ValueError(
                f"Need {counts[kind]} distinct {kind} backgrounds; available {len(pool)}"
            )
        for number, background in enumerate(pool[: counts[kind]]):
            recipe_seed = int(
                sha(f"{VERSION}:{seed}:{kind}:{number}:{background['image']}".encode())[
                    :8
                ],
                16,
            )
            plan.append((kind, number, background, recipe_seed))
    return plan


def atomic_text(path: Path, text: str) -> None:
    """Replace owned metadata atomically, after staging all image payloads."""
    temporary = path.with_name(path.name + ".synthetic-tmp")
    with temporary.open("x", encoding="utf-8") as file:
        file.write(text)
    os.replace(temporary, path)


def jsonl(rows: list[dict]) -> str:
    """Keep existing record values/order while appending synthetic provenance."""
    return "".join(json.dumps(r) + "\n" for r in rows)


def file_path(output: Path, relative: str) -> Path:
    """Constrain generated-data paths without resolving every read-only file."""
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Invalid dataset relative path: {relative}")
    return output / path


def real_snapshot(rows: list[dict], output: Path) -> str:
    """Fingerprint real records and every existing real payload's size/mtime."""
    result = hashlib.sha256(jsonl(rows).encode())
    for row in rows:
        for field in ("image", "label", "mask"):
            if row[field]:
                stat = file_path(output, row[field]).stat()
                result.update(
                    f"{row[field]}:{stat.st_size}:{stat.st_mtime_ns}\n".encode()
                )
    return result.hexdigest()


def heldout_snapshot(output: Path) -> str:
    """Hash the actual val/test file inventory and bytes across both tracks."""
    paths = sorted(
        p
        for prefix in ("", "anomaly", "classification_only")
        for kind in ("images", "labels", "masks")
        for split in ("val", "test")
        for p in (output / prefix / kind / split).rglob("*")
        if p.is_file()
    )

    def entry(path: Path) -> str:
        return path.relative_to(output).as_posix() + ":" + sha(path.read_bytes())

    with ThreadPoolExecutor(max_workers=8) as pool:
        return sha("\n".join(pool.map(entry, paths)).encode())


def verify_synthetic_rows(
    rows: list[dict], output: Path, payload_root: Path | None = None
) -> dict:
    """Validate provenance, exact insertion support, labels, and repeatability."""
    payload_root = payload_root or output
    real = {r["image"]: r for r in rows if not r.get("synthetic", False)}
    held_parents = {r["parent_id"] for r in rows if r["split"] != "train"}
    held_hashes = {r["pixel_sha256"] for r in rows if r["split"] != "train"}
    counts = Counter()
    for row in rows:
        if not row.get("synthetic", False):
            continue
        if (
            row["split"] != "train"
            or not row["augmented"]
            or row["source"] != "synthetic"
            or row["track"] != "multiclass"
            or row["generator"] != VERSION
        ):
            raise ValueError("Invalid synthetic identity/split")
        for field in ("image", "label", "mask"):
            path = Path(row[field])
            if path.parts[:2] != (
                field + "s" if field != "mask" else "masks",
                "train",
            ) or not path.name.startswith("synthetic_"):
                raise ValueError(
                    "Synthetic paths must be visibly tagged and train-only"
                )
        background = real[row["background_image"]]
        if (
            background["split"] != "train"
            or background["class_name"] != "normal"
            or background["classes"]
            or background["augmented"]
            or background["mask"]
            or row["parent_id"] != background["parent_id"]
            or row["pixel_sha256"] != background["pixel_sha256"]
            or row["background_source"] != background["source"]
            or row["parent_id"] in held_parents
            or row["pixel_sha256"] in held_hashes
        ):
            raise ValueError(
                "Synthetic background provenance is not train-only normal data"
            )
        bg_path = file_path(output, background["image"])
        if sha(bg_path.read_bytes()) != row["background_file_sha256"]:
            raise ValueError("Background changed since synthesis")
        bg = load_rgb(bg_path)
        expected, support, box, params = render_defect(
            bg, row["class_name"], row["augmentation_seed"]
        )
        actual = load_rgb(file_path(payload_root, row["image"]))
        stored = cv2.imread(
            str(file_path(payload_root, row["mask"])), cv2.IMREAD_GRAYSCALE
        )
        np.testing.assert_array_equal(actual, expected)
        np.testing.assert_array_equal(stored, support * 255)
        np.testing.assert_array_equal(actual[support == 0], bg[support == 0])
        if params != row["recipe_parameters"]:
            raise ValueError("Recipe parameters changed")
        boxes, classes = read_yolo(file_path(payload_root, row["label"]), 640, 640)
        np.testing.assert_allclose(boxes, [box], atol=1e-5)
        if classes != [NAMES.index(row["class_name"])]:
            raise ValueError("Synthetic class mismatch")
        verify_row(row, payload_root)
        counts[row["class_name"]] += 1
    return dict(counts)


def montage(rows: list[dict], output: Path, destination: Path) -> None:
    """Show background, unmarked synthesis, and annotated synthesis per class."""
    panels = []
    for kind in CLASSES:
        for row in [r for r in rows if r["class_name"] == kind][:3]:
            bg = load_rgb(file_path(output, row["background_image"]))
            generated = load_rgb(file_path(output, row["image"]))
            annotated = generated.copy()
            boxes, _ = read_yolo(file_path(output, row["label"]), 640, 640)
            x1, y1, x2, y2 = map(round, boxes[0])
            cv2.rectangle(
                annotated, (x1, y1), (min(639, x2), min(639, y2)), (255, 40, 40), 2
            )
            cv2.putText(
                annotated,
                "SYNTHETIC " + kind,
                (12, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 40, 40),
                2,
            )
            panels.append(
                np.concatenate(
                    [cv2.resize(im, (320, 320)) for im in (bg, generated, annotated)],
                    axis=1,
                )
            )
    if panels:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(
            str(destination), cv2.cvtColor(np.concatenate(panels), cv2.COLOR_RGB2BGR)
        ):
            raise OSError("Cannot save synthetic review montage")


def generate(
    output: Path,
    target: int = 200,
    minimum: int = 50,
    counts: dict | None = None,
    seed: int = 42,
    background_source: str = "zju_leaper",
) -> dict:
    """Append a deterministic, grow-only synthetic layer without changing real data."""
    cv2.setNumThreads(1)
    output = output.resolve()
    manifest = output / "manifest.jsonl"
    rows = [json.loads(s) for s in manifest.read_text().splitlines()]
    real = [r for r in rows if not r.get("synthetic", False)]
    synthetic = [r for r in rows if r.get("synthetic", False)]
    real_counts = Counter(
        r["class_name"]
        for r in real
        if r["track"] == "multiclass"
        and r["split"] == "train"
        and r["annotation_kind"] != "classification_only"
    )
    desired = {k: max(minimum, target - real_counts[k]) for k in CLASSES}
    desired.update(counts or {})
    if (
        target < 0
        or minimum < 0
        or any(
            k not in CLASSES or not isinstance(v, int) or v < 0
            for k, v in desired.items()
        )
    ):
        raise ValueError(
            "Counts must be nonnegative integers for the three supported classes"
        )
    config = {
        "version": VERSION,
        "seed": seed,
        "background_source": background_source,
        "real_manifest_sha256": sha(jsonl(real).encode()),
        "source_manifest_sha256": sha((output / "source-manifest.jsonl").read_bytes()),
        "generator_code_sha256": sha(Path(__file__).read_bytes()),
    }
    config_path = output / "synthetic-config.json"
    if synthetic:
        if not config_path.is_file() or json.loads(config_path.read_text()) != config:
            raise ValueError(
                "Synthetic recipe/base changed; use a separately rebuilt dataset, not in-place relabeling"
            )
        verified = verify_synthetic_rows(rows, output)
        if any(desired[k] < verified.get(k, 0) for k in CLASSES):
            raise ValueError("Refuse deleting synthetic samples; quotas may only grow")
        if all(desired[k] == verified.get(k, 0) for k in CLASSES):
            print("Existing synthetic layer verified; no files changed", flush=True)
            return json.loads((output / "synthetic-verification.json").read_text())
    plan = background_plan(real, desired, seed, background_source)
    existing = {(r["class_name"], r["synthetic_index"]) for r in synthetic}
    print(
        f"Real train counts: {dict(real_counts)}; synthetic quotas: {desired}",
        flush=True,
    )
    print("Snapshotting real-file metadata and held-out file contents", flush=True)
    before_real, before_held = real_snapshot(real, output), heldout_snapshot(output)
    stage = Path(tempfile.mkdtemp(prefix="_synthetic_stage_", dir=output))
    new = []
    for kind, index, bg, recipe_seed in plan:
        if (kind, index) in existing:
            continue
        bg_path = file_path(output, bg["image"])
        image, mask, box, params = render_defect(load_rgb(bg_path), kind, recipe_seed)
        stem = f"synthetic_{kind}_s{seed}_{index:05d}_{bg['pixel_sha256'][:10]}"
        row = {
            "image": f"images/train/{stem}.png",
            "label": f"labels/train/{stem}.txt",
            "mask": f"masks/train/{stem}.png",
            "synthetic": True,
            "generator": VERSION,
            "synthetic_index": index,
            "source": "synthetic",
            "background_source": bg["source"],
            "background_image": bg["image"],
            "background_file_sha256": sha(bg_path.read_bytes()),
            "parent_id": bg["parent_id"],
            "pixel_sha256": bg["pixel_sha256"],
            "raw": bg["raw"],
            "raw_label": "synthetic_" + kind,
            "class_name": kind,
            "source_class_name": "normal",
            "annotation_kind": "synthetic_mask",
            "augmented": True,
            "augmentation_seed": recipe_seed,
            "recipe_parameters": params,
            "split": "train",
            "track": "multiclass",
            "classes": [NAMES.index(kind)],
            "box_count": 1,
            "transform": bg["transform"],
            "native_split": bg["native_split"],
        }
        for field in ("image", "label", "mask"):
            destination = file_path(output, row[field])
            if (
                destination.exists()
                or output not in destination.parent.resolve().parents
            ):
                raise ValueError(
                    f"Refuse overwriting or escaping dataset: {destination}"
                )
            file_path(stage, row[field]).parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(
            str(stage / row["image"]),
            cv2.cvtColor(image, cv2.COLOR_RGB2BGR),
            [cv2.IMWRITE_PNG_COMPRESSION, 3],
        ):
            raise OSError("Image encoding failed")
        if not cv2.imwrite(str(stage / row["mask"]), mask * 255):
            raise OSError("Mask encoding failed")
        (stage / row["label"]).write_text(
            to_yolo([box], row["classes"]), encoding="utf-8"
        )
        verify_row(row, stage)
        new.append(row)
    verify_synthetic_rows(real + new, output, stage)
    # Publish only validated, newly named training files; recover on failure.
    combined = rows + new
    published = []
    try:
        for row in new:
            for field in ("image", "label", "mask"):
                source, destination = stage / row[field], output / row[field]
                source.rename(destination)
                published.append((source, destination))
        verified = verify_synthetic_rows(combined, output)
        after_real, after_held = real_snapshot(real, output), heldout_snapshot(output)
        if before_real != after_real or before_held != after_held:
            raise ValueError("Real or held-out files changed during synthesis")
    except Exception:
        for source, destination in reversed(published):
            destination.rename(source)
        raise
    previous = stage / "previous"
    previous.mkdir()
    for name in (
        "manifest.jsonl",
        "classification_train.jsonl",
        "synthetic-config.json",
        "synthetic-verification.json",
    ):
        if (output / name).is_file():
            shutil.copy2(output / name, previous / name)
    atomic_text(manifest, jsonl(combined))
    all_synthetic = synthetic + new
    atomic_text(output / "synthetic-manifest.jsonl", jsonl(all_synthetic))
    atomic_text(config_path, json.dumps(config, indent=2) + "\n")
    atomic_text(
        output / "classification_train.jsonl",
        jsonl(
            [
                r
                for r in combined
                if r["track"] == "multiclass" and r["split"] == "train"
            ]
        ),
    )
    for name, selection in (
        ("synthetic_train.txt", all_synthetic),
        (
            "real_train.txt",
            [
                r
                for r in real
                if r["track"] == "multiclass"
                and r["split"] == "train"
                and r["annotation_kind"] != "classification_only"
            ],
        ),
    ):
        atomic_text(output / name, "".join("./" + r["image"] + "\n" for r in selection))
    montage(all_synthetic, output, output / "_sanity_check" / "synthetic_contact.jpg")
    report = {
        "scope": "All synthetic outputs verified; real-file metadata and all val/test bytes unchanged",
        "generator": config,
        "synthetic_counts": verified,
        "real_train_image_counts": dict(real_counts),
        "combined_train_class_counts": dict(real_counts + Counter(verified)),
        "synthetic_images": len(all_synthetic),
        "output_images": len(combined),
        "multiclass_train_images": sum(
            r["track"] == "multiclass"
            and r["split"] == "train"
            and r["annotation_kind"] != "classification_only"
            for r in combined
        ),
        "real_file_metadata_sha256": after_real,
        "heldout_inventory_content_sha256": after_held,
        "manifest_sha256": sha(manifest.read_bytes()),
        "backup": previous.relative_to(output).as_posix(),
    }
    atomic_text(
        output / "synthetic-verification.json", json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2), flush=True)
    return report


def preview(output: Path, seed: int) -> None:
    """Render three examples per class for review before adding training data."""
    rows = [json.loads(s) for s in (output / "manifest.jsonl").read_text().splitlines()]
    panels = {k: [] for k in CLASSES}
    for kind, _, bg, recipe_seed in background_plan(
        rows, dict.fromkeys(CLASSES, 3), seed, "zju_leaper"
    ):
        background = load_rgb(output / bg["image"])
        generated, _, box, _ = render_defect(background, kind, recipe_seed)
        marked = generated.copy()
        x1, y1, x2, y2 = map(round, box)
        cv2.rectangle(marked, (x1, y1), (min(639, x2), min(639, y2)), (255, 40, 40), 2)
        cv2.putText(
            marked,
            "SYNTHETIC " + kind,
            (12, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 40, 40),
            2,
        )
        panels[kind].append(
            np.concatenate(
                [cv2.resize(im, (320, 320)) for im in (background, generated, marked)],
                axis=1,
            )
        )
    target = output / "_sanity_check"
    target.mkdir(exist_ok=True)
    for kind, images in panels.items():
        if not cv2.imwrite(
            str(target / f"synthetic_preview_{kind}.jpg"),
            cv2.cvtColor(np.concatenate(images), cv2.COLOR_RGB2BGR),
        ):
            raise OSError("Preview encoding failed")
    print("Preview only: no train/val/test data or manifests changed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "processed")
    parser.add_argument("--target-train", type=int, default=200)
    parser.add_argument("--minimum-synthetic", type=int, default=50)
    parser.add_argument("--counts", nargs="*", default=[], metavar="CLASS=N")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--background-source",
        choices=("zju_leaper", "aitex", "mvtec_ad", "all"),
        default="zju_leaper",
    )
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    if args.preview:
        preview(args.output.resolve(), args.seed)
    elif args.verify:
        records = [
            json.loads(s)
            for s in (args.output / "manifest.jsonl").read_text().splitlines()
        ]
        print(verify_synthetic_rows(records, args.output.resolve()))
    else:
        overrides = {k: int(v) for k, v in (item.split("=", 1) for item in args.counts)}
        generate(
            args.output,
            args.target_train,
            args.minimum_synthetic,
            overrides,
            args.seed,
            args.background_source,
        )
