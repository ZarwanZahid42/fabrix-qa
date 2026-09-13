# FabriX-QA detector — baseline v2 prototype

**Adopted:** 2026-09-13. `best.pt` is the fine-tuned YOLOv8n detector supplied
by Zarwan and the default model for image and file-video inference going forward.
Prototype detector training is complete; this is not a production acceptance or
completion of the CNN/autoencoder/fusion pipeline. Weights remain Git-ignored.

## Artifact identity and provenance

- File: `ai/models/best.pt`, 6,252,970 bytes.
- SHA-256: `d13aa10c5d724a8e5b431855ff241b4bd3dbf4ce17fb1f26cdb95e1939b8e376`.
- Embedded checkpoint date: **2026-09-12T20:28:14.397488+00:00**
  (2026-09-13 01:28:14 PKT). This is the checkpoint timestamp, not a claim
  about the exact start/end of every training epoch.
- Ultralytics checkpoint version: 8.4.133. Fine-tuned from `yolov8n.pt`;
  embedded configuration: image size 640, batch 8, AdamW, seed 42, 80 maximum
  epochs, patience 15, AMP enabled. Stripped checkpoint epoch is -1;
  actual epochs completed cannot be recovered from that field.
- **Naming discrepancy:** embedded run name remains
  `baseline_v1_20260912T195035Z_b9c437aa`. The v2 designation comes from
  Zarwan's explicit handoff, not that stale name. Do not rewrite the checkpoint.
- Intended dataset: the 2026-09-12 AITEX-tiled, synthetic-edge-revision-2 build,
  semantic train/val/test 4,607/210/208, 390 train-only synthetic examples.
  Local manifest SHA-256:
  `160705b5c2ba87051dbb2600f8db2d8f2863326575ed3847814195352d29705a`.
  The supplied checkpoint/report do not embed this hash; matching the actual
  Colab ZIP to it still needs `run_metadata.json`. It is an intended lineage,
  not a cryptographically verified training-data association.

## Supplied validation report

Exact values below come from `validation_metrics.json`, split **val**, not a
new local full evaluation. Overall **mAP50 = 0.7397368457536011**,
**mAP50-95 = 0.46414946906810284**. These supersede the rounded chat values.

| ID / class | Val images | AP50 | AP50-95 |
|---|---:|---:|---:|
| 0 hole | 38 | 0.8712318181290445 | 0.5719053828762928 |
| 1 weave_error | 68 | 0.6731388390517081 | 0.44320983683428217 |
| 2 stain | 10 | 0.9608333333333333 | 0.7230905315614617 |
| 3 foreign_object | 10 | 0.7993684210526317 | 0.5607219600725954 |
| 4 crease | 2 | 0.665 | 0.45483333333333337 |
| 5 edge_damage | 2 | 0.495 | 0.198 |
| 6 pattern_break | 15 | 0.7135855087084896 | 0.2972852387987549 |
| 7 aitex_unmapped | 0 | N/A | N/A |
| 8 tilda_unmapped | 0 | N/A | N/A |

Precision/recall are preserved in the JSON; edge_damage recall is 0.5. Reserved
IDs 7/8 have no training/validation evidence and must not be presented as learned
defect categories. The runtime checks the checkpoint's complete ID/name mapping
rather than relabeling an incompatible model.

Embedded checkpoint metrics differ slightly (mAP50 0.73909, mAP50-95 0.4638)
from the supplied separate validation report. No evaluation settings/run metadata
were supplied to establish why. Both records are preserved, not silently equated.
Finite saved validation metrics and successful inference do not prove every
training batch had finite loss; the historical v1 loss diagnosis remains open.

## Run locally (repository root, separate AI environment)

```powershell
.\ai\venv\Scripts\python.exe ai/inference/run_detection.py path/to/fabric.png artifacts/detection.png
.\ai\venv\Scripts\python.exe edge/stream_handler.py path/to/input.mp4 artifacts/annotated.mp4
.\ai\venv\Scripts\python.exe -m ai.inference.verify_detection --output artifacts/inference_v2_new
.\ai\venv\Scripts\python.exe -m unittest ai.inference.test_detection -v
```

Both entry points default to this checkpoint regardless of working directory.
Options: `--weights` (trusted local checkpoint only), `--device` (default CPU),
`--conf` (default 0.25). Shared inference uses 640-square letterboxing, IoU 0.7,
and returns boxes in original-frame pixel coordinates. These are prototype
thresholds, not calibrated quality policy. Missing weights or wrong class maps
fail explicitly; no pretrained download/fallback occurs. See the upstream
[prediction API](https://docs.ultralytics.com/modes/predict/) for BGR inputs and
original-image result conventions. Only trusted PyTorch files should be loaded.

Video processing loads one model, processes every frame without accumulating a
frame queue, draws class/confidence labels, and preserves dimensions/FPS. MP4
uses mp4v; AVI uses MJPG. Existing outputs are never overwritten. Odd dimensions,
invalid FPS, detectable truncation or codec failure are explicit errors. Outputs
are decoded fully before publication. Per-frame detections/timestamps and the
model hash live in `video_stage_*/frames.jsonl` and `summary.json` beside the
output. Failed staging artifacts remain for diagnosis. Audio is not preserved;
camera reconnect, live ROI/tiling, tracking, grading and backend delivery remain
unimplemented. Wide raw strips should not be taken as validated live inputs:
full-frame letterboxing can lose the small detail preserved by AITEX training tiles.

## Actual smoke verification and limits (2026-09-13)

- Loaded the supplied checkpoint on CPU; exact nine-name mapping confirmed.
- Fixed first two strong, real validation images per populated class (14 total),
  selected before predictions, at confidence 0.25: **13 predicted boxes**.
- No raw source video was found. A **28-frame slideshow of those real images**
  exercised video decoding/inference/encoding: **26 boxes on 18 frames**, all
  28 output frames decoded at 640x640 and 4 FPS. This is not factory-camera footage,
  tracking evidence or a real-time performance benchmark.
- Inspected the ground-truth/prediction sheet, native image outputs and decoded
  video frames. Hole/stain/foreign-object and some crease/pattern boxes localize
  visible defects with readable labels. There are genuine misses and confusions:
  one hole is labeled weave_error; one stain is labeled foreign_object; both
  selected weave examples and both edge examples are missed at 0.25; a crease
  has multiple overlapping predictions. No threshold/model changes were tuned
  against these observations, and no final-test images were used.
- Review artifacts: `artifacts/inference_v2/comparison.jpg`, `stain_1.png`,
  `video_frame_0.png`, `annotated.mp4`, and `verification.json` (all ignored).
- Five deterministic boundary/IO tests pass separately from real-weight checks.

Edge damage remains weakest and has only **two validation tiles from one source
strip**; small sample size makes its estimate unreliable, not a proven sole cause
of its low score. Crease is similarly scarce. Synthetic/domain bias, correlated
tiles, weak full-image rmshashi labels, coarse pattern-break mapping and missing
unseen-roll validation limit generalization. Keep v1 historical; use this v2 for
prototype work while collecting independent real edge evidence and planning a
controlled evaluation. CNN classification, autoencoder and heatmaps are still future work.
