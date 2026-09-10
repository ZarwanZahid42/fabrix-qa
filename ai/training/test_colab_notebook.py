"""Offline notebook/helper regression tests; never mount Drive or train a model."""

import ast
import contextlib
import io
import json
import shutil
import tempfile
import unittest
import uuid
import zipfile
from pathlib import Path
from types import SimpleNamespace

import nbformat
import yaml

NOTEBOOK = Path(__file__).with_name("colab_train_yolo.ipynb")


def helpers(cell: dict) -> dict:
    """Load only imports/functions, excluding the notebook's runtime calls."""
    tree = ast.parse("".join(cell["source"]))
    tree.body = [
        node
        for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef))
    ]
    namespace = {}
    # Execute only reviewed local helper definitions, never notebook runtime cells.
    exec(compile(tree, str(NOTEBOOK), "exec"), namespace)  # noqa: S102
    return namespace


class ColabNotebookTests(unittest.TestCase):
    def setUp(self):
        self.notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))

    def test_schema_order_empty_outputs_and_python_syntax(self):
        nbformat.validate(nbformat.from_dict(self.notebook))
        cells = self.notebook["cells"]
        self.assertEqual(len(cells), 9)
        self.assertEqual(
            [c["cell_type"] for c in cells],
            ["markdown"] + ["code"] * 7 + ["markdown"],
        )
        for cell in cells[1:8]:
            self.assertIsNone(cell["execution_count"])
            self.assertEqual(cell["outputs"], [])
            compile("".join(cell["source"]), cell["id"], "exec")
        training = "".join(cells[5]["source"])
        self.assertIn('YOLO("yolov8n.pt")', training)
        self.assertNotIn('YOLO("yolov8n.yaml")', training)
        self.assertIn('split="val"', "".join(cells[6]["source"]))

    def test_zip_extraction_rejects_traversal_and_nonempty_destination(self):
        extract = helpers(self.notebook["cells"][3])["extract_dataset"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "processed.zip"
            with zipfile.ZipFile(archive, "w") as out:
                out.writestr("../escape.txt", "bad")
            with self.assertRaises(ValueError):
                extract(archive, root / "output")
            with zipfile.ZipFile(archive, "w") as out:
                out.writestr("processed/data.yaml", "nc: 9")
                out.writestr("processed/_old/data.yaml", "nc: 1")
                out.writestr("processed/labels/train.cache", "stale")
            with contextlib.redirect_stdout(io.StringIO()):
                extract(archive, root / "output")
            self.assertTrue((root / "output/processed/data.yaml").is_file())
            self.assertFalse((root / "output/processed/_old").exists())
            with self.assertRaises(FileExistsError):
                extract(archive, root / "output")

    def test_counts_paths_manifest_and_synthetic_heldout_guard(self):
        inspect = helpers(self.notebook["cells"][4])["inspect_dataset"]
        names = [
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
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "processed"
            root.mkdir()
            original = yaml.safe_dump(
                {
                    "path": "C:/old/processed",
                    "names": dict(enumerate(names)),
                    "nc": 9,
                    **{s: f"images/{s}" for s in ("train", "val", "test")},
                }
            )
            (root / "data.yaml").write_text(original)
            rows = []
            for split in ("train", "val", "test"):
                (root / "images" / split).mkdir(parents=True)
                (root / "labels" / split).mkdir(parents=True)
                # Inventory/YOLO integrity is tested here, not image decoding.
                (root / "images" / split / "sample.png").write_bytes(b"fixture")
                (root / "labels" / split / "sample.txt").write_text(
                    "0 0.5 0.5 0.2 0.2\n0 0.2 0.2 0.1 0.1\n"
                )
                rows.append(
                    {
                        "image": f"images/{split}/sample.png",
                        "label": f"labels/{split}/sample.txt",
                        "split": split,
                        "parent_id": split,
                        "pixel_sha256": split,
                        "track": "multiclass",
                        "annotation_kind": "yolo",
                        "classes": [0, 0],
                        "box_count": 2,
                        "augmented": False,
                    }
                )
            manifest = root / "manifest.jsonl"
            manifest.write_text("\n".join(map(json.dumps, rows)))
            with contextlib.redirect_stdout(io.StringIO()):
                config, actual_names, counts = inspect(root, root.parent / "config")
            self.assertEqual(actual_names, names)
            self.assertEqual(counts["image_counts"]["train"]["hole"], 1)
            self.assertEqual(
                yaml.safe_load(config.read_text())["path"], str(root.resolve())
            )
            self.assertEqual((root / "data.yaml").read_text(), original)
            rows[1]["synthetic"] = True
            manifest.write_text("\n".join(map(json.dumps, rows)))
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(
                ValueError
            ):
                inspect(root, root.parent / "config")
            rows[1].pop("synthetic")
            rows[1]["parent_id"] = "train"
            manifest.write_text("\n".join(map(json.dumps, rows)))
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(
                ValueError
            ):
                inspect(root, root.parent / "config")

    def test_validation_class_indices_and_absent_classes(self):
        # Fixture metrics intentionally use a non-contiguous/out-of-order ID map.
        box = SimpleNamespace(
            map50=0.5,
            map=0.3,
            ap_class_index=[4, 0],
            class_result=lambda index: [(0.4, 0.3, 0.2, 0.1), (0.9, 0.8, 0.7, 0.6)][
                index
            ],
        )
        model = SimpleNamespace(val=lambda **kwargs: SimpleNamespace(box=box))
        with tempfile.TemporaryDirectory() as directory:
            scope = {
                "YOLO": lambda path: model,
                "BEST_WEIGHTS": "fixture.pt",
                "DATA_YAML": "fixture.yaml",
                "BATCH_SIZE": 8,
                "RUN_DIR": Path(directory),
                "NAMES": ["hole", "weave_error", "stain", "foreign_object", "crease"],
                "DATASET_SUMMARY": {"image_counts": {"val": {"hole": 10, "crease": 2}}},
                "json": json,
            }
            with contextlib.redirect_stdout(io.StringIO()):
                exec("".join(self.notebook["cells"][6]["source"]), scope)  # noqa: S102
            per_class = scope["VALIDATION_REPORT"]["per_class"]
            self.assertEqual(per_class["hole"]["precision"], 0.9)
            self.assertEqual(per_class["crease"]["precision"], 0.4)
            self.assertIsNone(per_class["stain"]["metrics"])

    def test_checkpoint_export_preserves_previous_copy_and_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            best = root / "run_best.pt"
            best.write_bytes(b"new fixture checkpoint")
            (root / "best.pt").write_bytes(b"previous fixture checkpoint")
            scope = {
                "DRIVE_ROOT": root,
                "RUN_DIR": root,
                "BEST_WEIGHTS": best,
                "RUN_METADATA": {},
                "shutil": shutil,
                "json": json,
                "uuid": uuid,
                "sha256_file": helpers(self.notebook["cells"][4])["sha256_file"],
            }
            with contextlib.redirect_stdout(io.StringIO()):
                exec("".join(self.notebook["cells"][7]["source"]), scope)  # noqa: S102
            self.assertEqual((root / "best.pt").read_bytes(), best.read_bytes())
            backups = list(root.glob("best_previous_*.pt"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), b"previous fixture checkpoint")


if __name__ == "__main__":
    unittest.main()
