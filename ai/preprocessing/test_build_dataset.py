"""Geometry and leakage regressions using small in-memory fixtures."""

import copy
import tempfile
import unittest
from pathlib import Path

import numpy as np
from build_dataset import (
    AITEX_TILING,
    ROOT,
    assign_splits,
    augment,
    convert_record,
    inspect_record,
    letterbox,
    load_mask,
    mask_boxes,
    plan_aitex_tiles,
    read_yolo,
    reconcile_tilda,
    tile_windows,
    to_yolo,
    verify_aitex_tiles,
    verify_row,
)
from PIL import Image


class DatasetTests(unittest.TestCase):
    def test_tile_windows_cover_full_strip_and_non_aligned_end(self):
        for width in (4096, 3796):
            windows = tile_windows(width, 256)
            cover = np.zeros(width, dtype=bool)
            for x1, y1, x2, y2 in windows:
                self.assertEqual((x2 - x1, y2 - y1), (256, 256))
                cover[x1:x2] = True
            self.assertTrue(cover.all())
            self.assertEqual(windows[-1][2], width)
            self.assertEqual(len(windows), len({tuple(w) for w in windows}))
        with self.assertRaises(ValueError):
            tile_windows(4096, 128)

    def test_aitex_tiling_clips_boundaries_and_preserves_lineage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pixels = np.zeros((256, 768, 3), np.uint8)
            mask = np.zeros((256, 768), np.uint8)
            mask[100:110, 250:260] = 255
            mask[5, 767] = 255
            pixels[mask > 0] = 255
            Image.fromarray(pixels).save(root / "image.png")
            Image.fromarray(mask).save(root / "mask.png")
            source = inspect_record(
                {
                    "source": "aitex",
                    "id": "aitex_fixture",
                    "path": str(root / "image.png"),
                    "raw": "image.png",
                    "masks": [str(root / "mask.png")],
                    "raw_label": "010",
                    "annotation_kind": "mask",
                    "class_name": "weave_error",
                    "track": "multiclass",
                    "native_split": None,
                    "split": "train",
                    "augmentations": 1,
                }
            )
            plan_aitex_tiles([source], 42)
            self.assertEqual(
                source["aitex_tiles"][0]["boxes"], [[250.0, 100.0, 256.0, 110.0]]
            )
            self.assertEqual(
                source["aitex_tiles"][1]["boxes"], [[58.0, 100.0, 68.0, 110.0]]
            )
            for kind in ("images", "labels", "masks"):
                (root / kind / "train").mkdir(parents=True)
            rows = convert_record(source, root, 42)
            for row in rows:
                self.assertEqual(row["parent_id"], source["id"])
                self.assertEqual(row["split"], "train")
                verify_row(row, root)
            verify_aitex_tiles([source], rows, root)
            self.assertEqual(len(rows), 6)
            self.assertTrue(
                any(
                    r.get("augmentation_policy") == "no_rotation_boundary_fallback"
                    for r in rows
                )
            )
            first_labels = {r["label"]: (root / r["label"]).read_bytes() for r in rows}
            repeated = convert_record(source, root, 42)
            self.assertEqual(rows, repeated)
            self.assertEqual(
                first_labels,
                {r["label"]: (root / r["label"]).read_bytes() for r in repeated},
            )

    def test_background_sampling_is_capped_deterministic_and_aitex_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mask = np.ones((256, 1024), np.uint8) * 255
            Image.fromarray(mask).save(root / "mask.png")
            records = [
                {
                    "id": "aitex_positive",
                    "source": "aitex",
                    "split": "train",
                    "original_wh": [1024, 256],
                    "annotation_kind": "mask",
                    "masks": [str(root / "mask.png")],
                }
            ]
            records += [
                {
                    "id": f"aitex_normal{i}",
                    "source": "aitex",
                    "split": "train",
                    "original_wh": [1024, 256],
                    "annotation_kind": "normal",
                    "masks": [],
                }
                for i in range(10)
            ]
            records += [
                {
                    "id": "unknown_position",
                    "source": "aitex",
                    "annotation_kind": "classification_only",
                },
                {"id": "other_source", "source": "tilda_400"},
            ]
            reversed_records = list(reversed(copy.deepcopy(records)))
            report = plan_aitex_tiles(records, 42)
            plan_aitex_tiles(reversed_records, 42)
            self.assertEqual(
                {r["id"]: r.get("aitex_tiles") for r in records},
                {r["id"]: r.get("aitex_tiles") for r in reversed_records},
            )
            counts = report["splits"]["train"]
            self.assertLessEqual(
                counts["sampled_backgrounds"],
                counts["positive_tiles"] * AITEX_TILING["backgrounds_per_positive"],
            )
            self.assertEqual(counts["sampled_backgrounds"], 1)
            self.assertNotIn("aitex_tiles", records[-1])
            self.assertNotIn("aitex_tiles", records[-2])
            selected_normal = next(
                r
                for r in records
                if r.get("annotation_kind") == "normal" and r["aitex_tiles"]
            )
            Image.fromarray(np.zeros((256, 1024, 3), np.uint8)).save(
                root / "normal.png"
            )
            selected_normal.update(
                {
                    "path": str(root / "normal.png"),
                    "raw": "normal.png",
                    "raw_label": "000",
                    "class_name": "normal",
                    "track": "multiclass",
                    "native_split": None,
                    "augmentations": 3,
                }
            )
            selected_normal = inspect_record(selected_normal)
            for kind in ("images", "labels", "masks"):
                (root / kind / "train").mkdir(parents=True)
            backgrounds = convert_record(selected_normal, root, 42)
            self.assertEqual(len(backgrounds), 1)
            self.assertFalse(backgrounds[0]["augmented"])
            self.assertEqual(backgrounds[0]["class_name"], "normal")
            self.assertEqual((root / backgrounds[0]["label"]).read_text(), "")
            verify_row(backgrounds[0], root)

    def test_downsample_preserves_single_pixel_defect(self):
        image = np.zeros((256, 4096, 3), np.uint8)
        mask = np.zeros((256, 4096), np.uint8)
        mask[123, 123] = 1
        _, _, transformed, _ = letterbox(image, [[123, 123, 124, 124]], mask)
        self.assertTrue(transformed.any())
        self.assertEqual(set(np.unique(transformed)), {0, 1})

    def test_tilda_repair_extends_thread_and_preserves_unmasked_box(self):
        mask = np.zeros((100, 100), np.uint8)
        mask[10:80, 10:20] = 1
        boxes = [[10.0, 10.0, 20.0, 30.0], [80.0, 80.0, 90.0, 90.0]]
        repaired, classes, notes = reconcile_tilda(boxes, [1, 1], mask)
        self.assertEqual(repaired[0], [10.0, 10.0, 20.0, 80.0])
        self.assertEqual(repaired[1], boxes[1])
        self.assertEqual(classes, [1, 1])
        self.assertEqual(notes["retained_boxes_without_mask_overlap"], 1)

    def test_default_dataset_directory_is_inside_ai(self):
        self.assertEqual(ROOT.name, "datasets")
        self.assertEqual(ROOT.parent.name, "ai")

    def test_submillipixel_export_rounding_is_clipped(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rounded.txt"
            path.write_text("1 0.2499995 0.25 0.5 0.5\n")
            boxes, _ = read_yolo(path, 768, 512)
        self.assertEqual(boxes[0][0], 0)

    def test_letterbox_box_roundtrip(self):
        image = np.zeros((256, 4096, 3), np.uint8)
        result, boxes, _, transform = letterbox(image, [[64, 32, 128, 96]])
        self.assertEqual(result.shape, (640, 640, 3))
        self.assertEqual(transform["pad_lt"], [0, 300])
        np.testing.assert_allclose(boxes, [[10, 305, 20, 315]])
        with tempfile.TemporaryDirectory() as directory:
            label = Path(directory) / "label.txt"
            label.write_text(to_yolo(boxes, [2]))
            decoded, classes = read_yolo(label, 640, 640)
        np.testing.assert_allclose(decoded, boxes)
        self.assertEqual(classes, [2])

    def test_union_masks_ignores_alpha_and_keeps_tiny_component(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for i, (y, x) in enumerate(((1, 1), (7, 7))):
                pixels = np.zeros((10, 10, 2), np.uint8)
                pixels[:, :, 1] = 255
                pixels[y, x, 0] = 255
                path = Path(directory) / f"mask{i}.png"
                Image.fromarray(pixels, mode="LA").save(path)
                paths.append(str(path))
            mask = load_mask(paths, (10, 10))
        self.assertEqual(int(mask.sum()), 2)
        self.assertEqual(mask_boxes(mask), [[1.0, 1.0, 2.0, 2.0], [7.0, 7.0, 8.0, 8.0]])

    def test_duplicates_stay_together_and_split_is_order_independent(self):
        rows = [
            {
                "source": "sample",
                "class_name": "hole",
                "pixel_sha256": str(i),
                "raw": str(i),
            }
            for i in range(20)
        ]
        rows.append(dict(rows[0]))
        reversed_rows = [dict(r) for r in reversed(rows)]
        report = assign_splits(rows, 42)
        assign_splits(reversed_rows, 42)
        self.assertEqual(report["duplicate_extra_images"], 1)
        self.assertEqual(rows[0]["split"], rows[-1]["split"])
        self.assertEqual(
            {r["raw"]: r["split"] for r in rows},
            {r["raw"]: r["split"] for r in reversed_rows},
        )
        self.assertEqual({r["split"] for r in rows}, {"train", "val", "test"})

    def test_augmentation_is_seeded_and_keeps_mask_aligned(self):
        image = np.zeros((640, 640, 3), np.uint8)
        image[100:200, 100:200] = 255
        mask = np.zeros((640, 640), np.uint8)
        mask[100:200, 100:200] = 1
        first = augment(image, [[100, 100, 200, 200]], [0], mask, 7)
        second = augment(image, [[100, 100, 200, 200]], [0], mask, 7)
        np.testing.assert_array_equal(first[0], second[0])
        np.testing.assert_allclose(first[1], second[1])
        xs, ys = np.where(first[3] > 0)[1], np.where(first[3] > 0)[0]
        x1, y1, x2, y2 = first[1][0]
        self.assertGreaterEqual(xs.min(), np.floor(x1) - 1)
        self.assertGreaterEqual(ys.min(), np.floor(y1) - 1)
        self.assertLessEqual(xs.max(), np.ceil(x2) + 1)
        self.assertLessEqual(ys.max(), np.ceil(y2) + 1)

    def test_invalid_yolo_rejected_and_normal_label_empty(self):
        self.assertEqual(to_yolo([], []), "")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.txt"
            path.write_text("0 0.1 0.1 1 1\n")
            with self.assertRaises(ValueError):
                read_yolo(path, 640, 640)


if __name__ == "__main__":
    unittest.main()
