"""Regression checks for label auditing and recoverable synthetic edge migration."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
from audit_yolo_labels import audit, check_box
from build_dataset import load_rgb, to_yolo
from refresh_synthetic_edge import refresh
from synthetic_defects import generate, jsonl, render_defect, sha
from test_synthetic_defects import background_record


class EdgeRevisionTests(unittest.TestCase):
    def test_audit_excludes_separate_classification_only_subset(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            (out / "labels/train").mkdir(parents=True)
            (out / "labels/train/normal.txt").write_text("")
            (out / "data.yaml").write_text("names: [hole]\nnc: 1\n")
            records = [
                {
                    "track": "multiclass",
                    "annotation_kind": "yolo",
                    "label": "labels/train/normal.txt",
                    "source": "fixture",
                },
                {
                    "track": "multiclass",
                    "annotation_kind": "classification_only",
                    "label": "classification_only/labels/train/positive.txt",
                },
            ]
            (out / "manifest.jsonl").write_text(jsonl(records))
            report = audit(out)
            self.assertEqual(report["invalid_count"], 0)
            self.assertEqual(report["label_files"], 1)

    def test_label_failures_and_positive_subpixel_warning_not_rejection(self):
        for text in (
            "0 .5 .5 0 .2",
            "0 .5 .5 .2 -1",
            "0 nan .5 .2 .2",
            "0 .5 .5 inf .2",
            "0 1.1 .5 .2 .2",
            "0 .99 .5 .2 .2",
            "9 .5 .5 .2 .2",
            "0 .5 .5",
        ):
            with self.subTest(text=text):
                self.assertTrue(check_box(text, 9))
        self.assertEqual(check_box("0 .5 .5 .0013 .0013", 9), [])
        self.assertEqual(check_box("0 .5 .5 1 1", 9), [])

    def test_edge_v2_has_both_styles_and_local_contrast(self):
        styles = set()
        for seed in range(12):
            bg = np.full((640, 640, 3), 30 if seed % 2 else 210, np.uint8)
            new, mask, box, params = render_defect(bg, "edge_damage", seed)
            styles.add(params["style"])
            self.assertGreaterEqual(
                abs(params["void_luminance"] - params["destination_mean"]), 99
            )
            np.testing.assert_array_equal(new[mask == 0], bg[mask == 0])
            self.assertGreater(box[2] - box[0], 0)
            self.assertGreater(box[3] - box[1], 0)
            self.assertEqual(params["edge_revision"], 2)
        self.assertEqual(styles, {"coherent_border_notch_v2", "inward_frayed_cut_v2"})

    def test_migration_rollback_then_success_preserves_other_payloads(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(
            io.StringIO()
        ):
            out = Path(directory)
            rows = [background_record(i) for i in range(30)]
            for r in rows:
                for key in ("image", "label"):
                    (out / r[key]).parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(
                    str(out / r["image"]), np.full((640, 640, 3), 100, np.uint8)
                )
                (out / r["label"]).write_text("")
            for folder in ("images", "labels", "masks"):
                (out / folder / "train").mkdir(parents=True)
            (out / "manifest.jsonl").write_text(jsonl(rows))
            (out / "source-manifest.jsonl").write_text(jsonl(rows))
            generate(
                out,
                minimum=0,
                counts={"crease": 1, "edge_damage": 1, "foreign_object": 1},
            )
            records = [
                json.loads(s) for s in (out / "manifest.jsonl").read_text().splitlines()
            ]
            edge = next(r for r in records if r["class_name"] == "edge_damage")
            old, mask, box, params = render_defect(
                load_rgb(out / edge["background_image"]),
                "edge_damage",
                edge["augmentation_seed"],
                edge_revision=1,
            )
            edge["recipe_parameters"] = params
            cv2.imwrite(str(out / edge["image"]), cv2.cvtColor(old, cv2.COLOR_RGB2BGR))
            cv2.imwrite(str(out / edge["mask"]), mask * 255)
            (out / edge["label"]).write_text(to_yolo([box], edge["classes"]))
            (out / "manifest.jsonl").write_text(jsonl(records))
            old_manifest = (out / "manifest.jsonl").read_bytes()
            original_payloads = {
                r[key]: sha((out / r[key]).read_bytes())
                for r in records
                for key in ("image", "label", "mask")
                if r[key]
            }
            with patch(
                "refresh_synthetic_edge.synthetic.real_snapshot",
                side_effect=["before", "changed"],
            ), self.assertRaises(ValueError):
                refresh(out)
            self.assertEqual((out / "manifest.jsonl").read_bytes(), old_manifest)
            for key, digest in original_payloads.items():
                self.assertEqual(sha((out / key).read_bytes()), digest)
            report = refresh(out)
            self.assertEqual(report["replaced_edge_images"], 1)
            for key, digest in original_payloads.items():
                if key not in {edge["image"], edge["label"], edge["mask"]}:
                    self.assertEqual(sha((out / key).read_bytes()), digest)
            self.assertEqual(
                (out / report["backup"] / edge["image"]).read_bytes(),
                cv2.imencode(".png", cv2.cvtColor(old, cv2.COLOR_RGB2BGR))[1].tobytes(),
            )
            self.assertEqual(refresh(out)["edge_revision"], 2)


if __name__ == "__main__":
    unittest.main()
