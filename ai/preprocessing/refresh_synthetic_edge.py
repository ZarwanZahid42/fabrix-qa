"""Explicit, recoverable migration of synthetic edge v1 to v2; no other data edits."""

import argparse
import json
import shutil
import tempfile
from pathlib import Path

import cv2
import numpy as np
import synthetic_defects as synthetic
from build_dataset import ROOT, load_rgb, to_yolo


def review(output: Path) -> None:
    """Render fixed training examples as background/old/v2/v2 with box."""
    rows = [json.loads(s) for s in (output / "manifest.jsonl").read_text().splitlines()]
    edges = [r for r in rows if r.get("synthetic") and r["class_name"] == "edge_damage"]
    panels = []
    for row in edges[:: max(1, len(edges) // 5)][:5]:
        bg = load_rgb(output / row["background_image"])
        new, _, box, _ = synthetic.render_defect(
            bg, "edge_damage", row["augmentation_seed"]
        )
        marked = new.copy()
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(marked, (x1, y1), (min(639, x2), min(639, y2)), (255, 0, 0), 2)
        columns = []
        for title, image in zip(
            (
                "TRAIN background",
                "Existing synthetic",
                "Proposed edge v2",
                "v2 insertion box",
            ),
            (bg, load_rgb(output / row["image"]), new, marked),
            strict=True,
        ):
            tile = cv2.resize(image, (320, 320))
            cv2.putText(
                tile, title, (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 1
            )
            columns.append(tile)
        panels.append(np.concatenate(columns, axis=1))
    if not panels:
        raise ValueError("No synthetic edges found")
    path = output / "_sanity_check/edge_v2_comparison.jpg"
    path.parent.mkdir(exist_ok=True)
    if not cv2.imwrite(
        str(path), cv2.cvtColor(np.concatenate(panels), cv2.COLOR_RGB2BGR)
    ):
        raise OSError("Review image write failed")
    print(path)


def refresh(output: Path) -> dict:
    """Stage exact masks/boxes, archive v1, replace only validated train edges."""
    cv2.setNumThreads(1)
    output = output.resolve()
    rows = [json.loads(s) for s in (output / "manifest.jsonl").read_text().splitlines()]
    edges = [r for r in rows if r.get("synthetic") and r["class_name"] == "edge_damage"]
    if not edges:
        raise ValueError("No existing synthetic edge layer")
    synthetic.verify_synthetic_rows(
        rows, output
    )  # Supports recorded v1 and v2 recipes.
    if all(r["recipe_parameters"].get("edge_revision") == 2 for r in edges):
        print("Edge v2 already verified; no files changed")
        return json.loads((output / "synthetic-verification.json").read_text())
    if any(r["recipe_parameters"].get("edge_revision", 1) != 1 for r in edges):
        raise ValueError("Mixed edge revisions; investigate partial migration")
    real = [r for r in rows if not r.get("synthetic")]
    config = json.loads((output / "synthetic-config.json").read_text())
    if config["real_manifest_sha256"] != synthetic.sha(
        synthetic.jsonl(real).encode()
    ) or config["source_manifest_sha256"] != synthetic.sha(
        (output / "source-manifest.jsonl").read_bytes()
    ):
        raise ValueError("Real base differs from recorded synthetic input")
    edge_paths = {r["image"] for r in edges}
    protected = [r for r in rows if r["image"] not in edge_paths]
    print(
        "Snapshotting all non-edge payload metadata and every held-out file byte",
        flush=True,
    )
    before_real = synthetic.real_snapshot(protected, output)
    before_held = synthetic.heldout_snapshot(output)
    stage = Path(tempfile.mkdtemp(prefix="_edge_v2_", dir=output))
    previous = stage / "previous"
    previous.mkdir()
    metadata_names = (
        "manifest.jsonl",
        "synthetic-manifest.jsonl",
        "classification_train.jsonl",
        "synthetic-config.json",
        "synthetic-verification.json",
        "verification.json",
        "ultralytics-verification.json",
    )
    for name in metadata_names:
        if (output / name).exists():
            shutil.copy2(output / name, previous / name)
    replacements = {}
    for row in edges:
        image, mask, box, params = synthetic.render_defect(
            load_rgb(output / row["background_image"]),
            "edge_damage",
            row["augmentation_seed"],
        )
        new = dict(row, recipe_parameters=params)
        replacements[row["image"]] = new
        for field in ("image", "label", "mask"):
            # Resolve and confine every moved file BEFORE publishing any changes.
            live = synthetic.file_path(output, row[field]).resolve()
            if not live.is_relative_to(output) or not live.is_file():
                raise ValueError(f"Unsafe/missing migration target: {live}")
            (stage / row[field]).parent.mkdir(parents=True, exist_ok=True)
            (previous / row[field]).parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(
            str(stage / row["image"]),
            cv2.cvtColor(image, cv2.COLOR_RGB2BGR),
            [cv2.IMWRITE_PNG_COMPRESSION, 3],
        ):
            raise OSError("Staged image encoding failed")
        if not cv2.imwrite(str(stage / row["mask"]), mask * 255):
            raise OSError("Staged mask encoding failed")
        (stage / row["label"]).write_text(
            to_yolo([box], row["classes"]), encoding="utf-8"
        )
    synthetic.verify_synthetic_rows(real + list(replacements.values()), output, stage)
    updated = [replacements.get(r["image"], r) for r in rows]
    moved = []
    try:
        for row in edges:
            for field in ("image", "label", "mask"):
                relative = row[field]
                (output / relative).rename(previous / relative)
                moved.append(relative)
                (stage / relative).rename(output / relative)
        verified = synthetic.verify_synthetic_rows(updated, output)
        if (
            synthetic.real_snapshot(protected, output) != before_real
            or synthetic.heldout_snapshot(output) != before_held
        ):
            raise ValueError("Non-edge or held-out payload changed")
        config["generator_code_sha256"] = synthetic.sha(
            Path(synthetic.__file__).read_bytes()
        )
        synthetic.atomic_text(output / "manifest.jsonl", synthetic.jsonl(updated))
        synthetic.atomic_text(
            output / "synthetic-manifest.jsonl",
            synthetic.jsonl([r for r in updated if r.get("synthetic")]),
        )
        synthetic.atomic_text(
            output / "classification_train.jsonl",
            synthetic.jsonl(
                [
                    r
                    for r in updated
                    if r["track"] == "multiclass" and r["split"] == "train"
                ]
            ),
        )
        synthetic.atomic_text(
            output / "synthetic-config.json", json.dumps(config, indent=2) + "\n"
        )
        report = json.loads((previous / "synthetic-verification.json").read_text())
        report.update(
            {
                "generator": config,
                "synthetic_counts": verified,
                "manifest_sha256": synthetic.sha(
                    (output / "manifest.jsonl").read_bytes()
                ),
                "edge_revision": 2,
                "replaced_edge_images": len(edges),
                "previous_manifest_sha256": synthetic.sha(
                    (previous / "manifest.jsonl").read_bytes()
                ),
                "unchanged_non_edge_metadata_sha256": before_real,
                "heldout_inventory_content_sha256": before_held,
                "backup": previous.relative_to(output).as_posix(),
            }
        )
        synthetic.atomic_text(
            output / "synthetic-verification.json", json.dumps(report, indent=2) + "\n"
        )
    except Exception:
        for relative in reversed(moved):
            if (output / relative).exists():
                (output / relative).rename(stage / relative)
            (previous / relative).rename(output / relative)
        for name in metadata_names:
            if (previous / name).exists():
                shutil.copy2(previous / name, output / name)
        raise
    synthetic.montage(
        [r for r in updated if r.get("synthetic")],
        output,
        output / "_sanity_check/synthetic_contact.jpg",
    )
    print(json.dumps(report, indent=2), flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "processed")
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    if args.preview:
        review(args.output.resolve())
    else:
        refresh(args.output)
