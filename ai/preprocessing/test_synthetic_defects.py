"""Synthetic geometry, leakage, provenance and append-only integration tests."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
from build_dataset import require_real_only_output
from synthetic_defects import (
    CLASSES,
    background_plan,
    eligible_backgrounds,
    generate,
    heldout_snapshot,
    jsonl,
    render_defect,
    sha,
    verify_synthetic_rows,
)


def background_record(index: int, split: str = "train") -> dict:
    """Create realistic manifest fields without needing the external datasets."""
    return {
        "image": f"anomaly/images/{split}/zju_{index}.png",
        "label": f"anomaly/labels/{split}/zju_{index}.txt",
        "mask": None,
        "parent_id": f"zju_{index}",
        "pixel_sha256": sha(str(index).encode()),
        "source": "zju_leaper",
        "class_name": "normal",
        "classes": [],
        "split": split,
        "track": "anomaly",
        "augmented": False,
        "annotation_kind": "normal",
        "box_count": 0,
        "raw": f"zju_leaper/Images/{index}.jpg",
        "raw_label": 0,
        "native_split": split,
        "transform": {
            "original_wh": [512, 512],
            "resized_wh": [640, 640],
            "pad_lt": [0, 0],
        },
    }


class SyntheticTests(unittest.TestCase):
    def test_base_rebuild_refuses_existing_synthetic_layer(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            require_real_only_output(output)
            (output / "synthetic-config.json").write_text("{}")
            with self.assertRaises(ValueError):
                require_real_only_output(output)

    def test_render_is_seeded_localized_and_does_not_modify_background(self):
        background = np.random.default_rng(1).integers(
            50, 210, (640, 640, 3), dtype=np.uint8
        )
        original = background.copy()
        for kind in CLASSES:
            for seed in range(4):
                with self.subTest(kind=kind, seed=seed):
                    image, mask, box, params = render_defect(background, kind, seed)
                    repeated = render_defect(background, kind, seed)
                    np.testing.assert_array_equal(image, repeated[0])
                    np.testing.assert_array_equal(mask, repeated[1])
                    self.assertEqual(params, repeated[3])
                    np.testing.assert_array_equal(background, original)
                    np.testing.assert_array_equal(
                        image[mask == 0], background[mask == 0]
                    )
                    yy, xx = np.where(mask)
                    self.assertEqual(
                        box, [xx.min(), yy.min(), xx.max() + 1, yy.max() + 1]
                    )
                    self.assertGreater(int(mask.sum()), 8)
                    self.assertLess(int(mask.sum()), 640 * 640 * 0.15)
                    if kind == "edge_damage":
                        self.assertTrue(
                            box[0] == 0 or box[1] == 0 or box[2] == 640 or box[3] == 640
                        )

    def test_invalid_shape_and_class_are_rejected(self):
        with self.assertRaises(ValueError):
            render_defect(np.zeros((32, 32, 3), np.uint8), "crease", 0)
        with self.assertRaises(ValueError):
            render_defect(np.zeros((640, 640, 3), np.uint8), "hole", 0)

    def test_heldout_background_and_hash_leakage_rejected(self):
        good = background_record(1)
        heldout = background_record(2, "val")
        self.assertEqual(eligible_backgrounds([heldout, good], "zju_leaper"), [good])
        heldout["pixel_sha256"] = good["pixel_sha256"]
        with self.assertRaises(ValueError):
            eligible_backgrounds([heldout, good], "zju_leaper")

    def test_normal_selection_excludes_augmentation_defects_and_padding(self):
        good = background_record(1)
        invalid = [copy.deepcopy(background_record(i)) for i in range(2, 6)]
        invalid[0]["augmented"] = True
        invalid[1]["classes"] = [0]
        invalid[2]["synthetic"] = True
        invalid[3]["transform"]["pad_lt"] = [0, 100]
        self.assertEqual(eligible_backgrounds(invalid + [good], "zju_leaper"), [good])

    def test_partitions_are_disjoint_and_quota_growth_keeps_old_recipes(self):
        rows = [background_record(i) for i in range(100)]
        first = background_plan(rows, dict.fromkeys(CLASSES, 2), 42, "zju_leaper")
        grown = background_plan(
            list(reversed(rows)), dict.fromkeys(CLASSES, 3), 42, "zju_leaper"
        )
        self.assertEqual(len({r[2]["parent_id"] for r in grown}), 9)
        self.assertEqual(first, [r for r in grown if r[1] < 2])
        with self.assertRaises(ValueError):
            background_plan(rows, dict.fromkeys(CLASSES, 1000), 42, "zju_leaper")

    def test_pipeline_is_train_only_idempotent_and_grow_only(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            rows = [background_record(i) for i in range(30)]
            rows += [background_record(90, "val"), background_record(91, "test")]
            for row in rows:
                for key in ("image", "label"):
                    (output / row[key]).parent.mkdir(parents=True, exist_ok=True)
                image = np.full(
                    (640, 640, 3), 80 + int(row["parent_id"].split("_")[1]), np.uint8
                )
                self.assertTrue(cv2.imwrite(str(output / row["image"]), image))
                (output / row["label"]).write_text("")
            for kind in ("images", "labels", "masks"):
                (output / kind / "train").mkdir(parents=True)
            (output / "manifest.jsonl").write_text(jsonl(rows))
            (output / "source-manifest.jsonl").write_text(jsonl(rows))
            (output / "strong_train.txt").write_text("unchanged real-only list\n")
            heldout_before = heldout_snapshot(output)
            first = generate(output, minimum=0, counts=dict.fromkeys(CLASSES, 1))
            self.assertEqual(first["synthetic_images"], 3)
            self.assertEqual(first["heldout_inventory_content_sha256"], heldout_before)
            self.assertEqual(
                (output / "strong_train.txt").read_text(), "unchanged real-only list\n"
            )
            manifest = (output / "manifest.jsonl").read_bytes()
            generate(output, minimum=0, counts=dict.fromkeys(CLASSES, 1))
            self.assertEqual(manifest, (output / "manifest.jsonl").read_bytes())
            grown = generate(output, minimum=0, counts=dict.fromkeys(CLASSES, 2))
            self.assertEqual(grown["synthetic_images"], 6)
            final = [
                json.loads(line)
                for line in (output / "manifest.jsonl").read_text().splitlines()
            ]
            self.assertEqual(final[: len(rows)], rows)
            self.assertEqual(
                verify_synthetic_rows(final, output), dict.fromkeys(CLASSES, 2)
            )
            self.assertEqual(heldout_snapshot(output), heldout_before)
            with self.assertRaises(ValueError):
                generate(output, minimum=0, counts=dict.fromkeys(CLASSES, 1))
            with self.assertRaises(ValueError):
                generate(output, minimum=0, counts=dict.fromkeys(CLASSES, 2), seed=7)
            final[-1]["split"] = "val"
            with self.assertRaises(ValueError):
                verify_synthetic_rows(final, output)


if __name__ == "__main__":
    unittest.main()
