# FabriX-QA dataset manifest

Audited 2026-09-05 on features/zarwan. Counts describe the local copies, not advertised sizes. Raw and processed payloads are Git-ignored. No model has been trained. The real-data baseline is documented separately from the explicitly tagged synthetic training extension below.

## Source inventory (before conversion)

| Source | Actual images | Annotation evidence | Dimensions |
|---|---:|---|---|
| rmshashi | 666 | Folder labels: 281 hole, 385 weave-error images | JPEG: 412 at 640x360, 232 at 1280x720, 22 at 4608x3456 |
| AITEX | 247 | 106 defective, 141 normal; 107 masks, one entirely zero; 104 usable localized defective images | Mostly 4096x256; one defective image/mask 3796x256 |
| TILDA-400 | 400 (+2 references) | 400 YOLO files, 400 masks, 514 boxes; all 400 labeled images defective | TIFF images and PNG masks 768x512 |
| ZJU-Leaper | 94,833 | 94,833 XML; 71,127 normal, 23,706 defective; 23,706 masks, 35,675 XML boxes | All images decoded: 512x512 |
| MVTec carpet/grid | 739 | Carpet 397 images/89 masks; grid 342 images/57 masks | 1024x1024 PNG |

All five folders are extracted and non-empty. Other MVTec categories are excluded. TILDA's two root reference TIFFs remain raw reference assets, not labeled training examples.

## Attribution and documented research

- rmshashi: <https://www.kaggle.com/datasets/rmshashi/fabric-defect-dataset>. Actual leaves: `Data Set/hole` 184, `horizontal` 136, `verticle` 92, `captured/Hole` 97, `captured/Lines` 157. No defect_free or stain folder exists.
- AITEX Kaggle reference: <https://www.kaggle.com/datasets/nexuswho/aitex-fabric-image-database>. Original <https://www.aitex.es/afid/> was unavailable during research. **Resolved via documented dataset research:** Silvestre-Blanes et al., *A Public Fabric Database for Defect Detection Methods and Results* (2019), DOI 10.2478/aut-2019-0035, Table 1 (journal page 364), available at <https://riunet.upv.es/server/api/core/bitstreams/52d318c8-921f-4172-ad2f-889effa7dd15/content>. The middle filename token is the defect code; the last is fabric. Local count 247 differs from advertised 245.
- TILDA: <https://www.kaggle.com/datasets/angelolmg/tilda-400>, original resource <https://lmb.informatik.uni-freiburg.de/resources/datasets/tilda.en.html>. **Resolved via documented dataset research:** subset publisher defines IDs 0 hole, 1 foreign object/contamination, 2 oil stain, 3 thread-related defect. The publisher acknowledges semantic interpretation of original error codes; this is not claimed to be an authoritative original German class dictionary. Actual boxes: ID0=112, ID1=126, ID2=122, ID3=154; 100 images per ID. Earlier publisher counts differ. This is the full-image version, not tilda-400-64x64-patches.
- ZJU: bundled README, statistic.csv, XML/JSON; <http://www.qaas.zju.edu.cn/zju-leaper/> and <https://github.com/nico-zck/ZJU-Leaper-Dataset/tree/master/dataset_api>. 19 patterns and 5 groups; binary labels only.
- MVTec: bundled carpet/grid readme/license files; <https://www.mvtec.com/company/research/datasets/mvtec-ad>. Cite Bergmann et al., *A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection*, CVPR 2019.

rmshashi, AITEX and TILDA have no bundled license: documented gap, academic/FYP preprocessing authorized by Zarwan based on prior vetting. Kaggle links are attribution references; exact download versions are not independently recorded. TILDA's publisher and bundled ZJU/MVTec licenses state CC BY-NC-SA 4.0; ZJU also states academic use/citation. This does not establish commercial deployment rights.

## Taxonomy and decisions

Stable detector IDs: 0 hole, 1 weave_error, 2 stain, 3 foreign_object, 4 crease, 5 edge_damage, 6 pattern_break, 7 aitex_unmapped, 8 tilda_unmapped. Normal images have empty YOLO labels, never normal boxes. The two reserved unmapped buckets currently have zero source samples.

| AITEX code | Documented name | Images | Unified class |
|---|---|---:|---|
| 002 | Broken end | 9 | weave_error |
| 006 | Broken yarn | 8 | weave_error |
| 010 | Broken pick | 10 | weave_error |
| 016 | Weft curling | 3 | weave_error |
| 019 | Fuzzy ball | 39 | weave_error |
| 022 | Cut selvage | 9 | edge_damage |
| 023 | Crease | 5 | crease |
| 025 | Warp ball | 6 | weave_error |
| 027 | Knots | 1 | weave_error |
| 029 | Contamination | 1 | foreign_object |
| 030 | Nep | 14 | weave_error |
| 036 | Weft crack | 1 | weave_error |

The names above are researched; the broad merges are project decisions. Yarn irregularities merge into weave_error. Crease and cut selvage remain separate; contamination is foreign_object without assuming oil. Original codes/names survive in manifests. OR multiple masks for 0044_019_04 and 0097_030_03 before component extraction. Keep maskless 0100_025_08 (warp ball) as classification-only, excluded from localization. The pixel audit additionally found 0106_010_03 (broken pick) has a completely black mask: apply the same classification-only policy. No replacement mask or negative detection label is fabricated for these positive samples.

TILDA maps 0->hole, 1->foreign_object, 2->stain, 3->weave_error. **Stain has 100 TILDA source images**, correcting the earlier assumption of zero coverage. rmshashi hole and captured/Hole merge into hole; horizontal, verticle (normalized source label vertical), captured/Lines merge into weave_error, per explicit user rules. Image-level labels become **weak full-image boxes** that do not establish true boundaries. Captured/top-level samples may overlap; duplicate grouping cannot prove all near-duplicates are absent.

MVTec carpet/grid defects map to pattern_break as the requested texture-anomaly proxy, with original subtypes retained. This coarse project mapping does not assert that cuts, metal and glue are the same physical defect. Carpet: color19, cut17, hole17, metal_contamination17, thread19; grid: bent12, broken12, glue11, metal_contamination11, thread11. Normal total 593.

**Native ZJU examples remain excluded from multiclass detector/classifier training.** Its separate anomaly track retains binary status and localization. The explicitly authorized exception is a tagged synthetic derivative: normal, original ZJU training backgrounds can receive procedural defects with known insertion labels. No semantic defect type is inferred from ZJU's binary annotation. Future normal-only autoencoder training must still use its normal-training manifest, not all images in anomaly/images/train or the synthetic derivatives.

**Unmapped/bucketed:** none of the observed AITEX/TILDA IDs remains unresolved. Fallback buckets remain explicit for future unknown codes.

## Processing contract

Target 80/10/10 at original source-image level before augmentation, stratified by source and class. Exact decoded duplicates share a split; augmented copies inherit parents. Group sizes can alter exact ratios. Custom FYP splits replace official benchmark splits; preserve native split provenance and do not claim official benchmark scores. Same-image grouping cannot establish unseen-roll generalization where roll identity is absent.

Letterbox images to 640x640 preserving aspect ratio. Mask foreground uses luminance, not alpha; OR masks and extract connected-component rectangles without an area cutoff. Binary mask downsampling uses area occupancy (any contributing foreground remains positive), not nearest-neighbor sampling that erased thin AITEX defects during verification. Upsampling uses nearest neighbor; boxes retain exact subpixel geometry. This conservatively preserves mask evidence but cannot recover image detail lost through downscaling. Augment train only with horizontal flip, brightness/contrast and slight rotation; minority quotas derive only from training counts.

### TILDA annotation repair (project quality decision)

Supplied YOLO boxes are retained in source manifests. Two coordinates in c1r1e4n16 extend less than 0.001 pixel past an edge from decimal rounding; clip only that tolerance. Direct image/box/mask overlays showed a truncated thread box (c1r1e3n8 covers only 47.75% of mask pixels), while c1r1e1n43 has a plausible extra boundary hole box absent from its mask. Therefore keep original boxes, expand each to enclose its best-overlapping connected mask region, and add any completely uncovered mask component using the image's single class. Preserve original boxes without mask overlap; do not erase potentially real defects merely because one annotation omits them. Record expansions, additions and unmatched boxes per image. This conservative union repairs localization without changing semantic class IDs or raw files. Diagnostic comparisons are in ignored inspection/.

The complete source decode/hash audit found 13 exact duplicate pairs, all within rmshashi and with consistent labels. Both members share one split and remain traceable; no claim is made that alternate crops or near-duplicates are exhausted.

### AITEX native-resolution tiling

AITEX detection now uses **256x256 native-pixel square tiles**, stride **192**
(25% overlap), resized to 640x640. The last tile is anchored to the right edge
so a non-stride-aligned strip end is fully covered; its overlap can be larger.
256 matches the actual strip height, avoiding padding or the previous
4096x256 -> 640x40 reduction. This gives 2.5 output pixels per native pixel
instead of 0.15625 (16 times the previous linear detail for 4096-wide strips).
It preserves existing visual detail, not new physical resolution.

OR masks before cropping. For each crop, connected foreground regions yield
tight local rectangles, including partial defects at tile edges; the source
offset is removed before scaling and YOLO normalization. Empty portions of a
global bounding rectangle do not create false positive tiles. Keep every tile
with any foreground (no minimum-area filter), ensuring the union of retained
positive crops covers every annotated source defect pixel.

Sample at most floor(positive_tile_count / 4) pure-background tiles **per split**
before augmentation. Selection is seeded and round-robin across eligible strips,
using both normal strips and mask-empty crops of annotated defective strips.
All remaining empty tiles are omitted and counted. Sampled backgrounds receive
empty YOLO files and class_name=normal, never the defective parent class, and
are **not augmented**. The 80/10/10 source-image split and existing exact-duplicate
groups are fixed before tiling; all overlapping tiles/copies inherit the parent's
split. This creates a curated tile evaluation distribution, not natural fabric
prevalence or independent strip-level samples.

Positive training tiles retain the previously assigned source-class augmentation
quota. If rotation removes a box or leaves a labeled region without mask pixels,
an AITEX-only seeded flip/brightness fallback omits rotation; its policy is logged
per copy. Other sources' transforms and quotas are unchanged. The two positive
strips without valid localization remain untiled classification-only samples:
no tiles are guessed positive or negative from an unknown defect location.

`source-manifest.jsonl` records selected windows/local boxes per strip;
`manifest.jsonl` records tile ID, parent ID/hash, native window, transform,
source class, actual tile class and augmentation seed/policy. Normal strips
with no sampled tile remain in the source audit, with an empty tile selection.
`aitex-tiling.json` records candidate/kept/discarded counts and rebuild provenance.

## Reproduce and verify

From the repository root on Windows, using the existing separate AI environment:

```powershell
.\ai\venv\Scripts\python.exe ai/preprocessing/build_dataset.py --workers 8
.\ai\venv\Scripts\python.exe ai/preprocessing/build_dataset.py --verify --workers 8
.\ai\venv\Scripts\python.exe ai/preprocessing/verify_ultralytics.py
.\ai\venv\Scripts\python.exe -m unittest discover -s ai/preprocessing -p test_build_dataset.py -v
```

To replace only AITEX in an existing processed dataset while preserving the
other four sources, run `build_dataset.py --rebuild-aitex`, then `--verify`
and `verify_ultralytics.py` using the same AI Python executable. The scoped
rebuild stages and validates AITEX first, reuses audited splits/quotas, refuses
changed raw images/annotations, and archives its previous generated files and
manifests under ignored `processed/_aitex_rebuild_*/previous/`. No raw files are
removed; archived files are outside YOLO image/label trees and active counts.
This command, not a legacy `--resume`, migrates the full-strip build to tiling.

On other platforms use the AI environment's Python executable. Default seed is
42. The builder refuses a nonempty output directory unless explicitly given
`--resume` with a matching build-config.json. Resume reprocesses inputs; it does
not delete output files. Use a fresh `--output` directory when changing seed,
source membership or augmentation policy. YAML paths are generated for the
current machine. The verification loop's `--refresh-semantic` command can refresh
the small semantic sources after annotation-code corrections, preserving splits
and copy counts and refusing changed source pixels; it leaves ZJU outputs alone.
A fresh build already includes reconciliation. Always run complete verification afterward.

Generated layout (all ignored):

```text
processed/
  images/{train,val,test}/       # multiclass detector images
  labels/{train,val,test}/       # one YOLO file per image; normals are empty
  masks/{train,val,test}/        # where source masks exist
  data.yaml                     # 7 populated semantic classes + 2 reserved IDs
  anomaly/
    images/{train,val,test}/     # ZJU binary track, including normals
    labels/{train,val,test}/     # defect=0; normal files are empty
    masks/{train,val,test}/      # defective mask evidence
    data.yaml
    normal_{train,val,test}.txt  # ONLY normals; paths relative to anomaly/
  classification_only/          # two AITEX positives without valid localization
  classification_{train,val,test}.jsonl
  strong_{train,val,test}.txt    # real-only; excludes weak, classification-only, synthetic
  synthetic-manifest.jsonl      # explicit synthetic provenance and insertion recipes
  synthetic-config.json
  synthetic-verification.json  # extension verification and current combined counts
  synthetic_train.txt           # synthetic-only training ablation list
  real_train.txt                # non-synthetic detector train images, including ordinary augmentation
  source-manifest.jsonl         # raw/annotation hashes, pixels, boxes, source labels
  manifest.jsonl                # outputs, parent, split, transforms and copy seeds
  build-config.json
  audit.json
  verification.json
  ultralytics-verification.json
  _sanity_check/                # five annotated originals per source + metadata
```

Classification manifests reference images and semantic names; they are not a
YOLO classification-folder export. They contain **no native ZJU samples**;
tagged synthetic derivatives may use ZJU training backgrounds. The two
classification-only images have no localization target and never appear under
the detector's images/ tree. Normal semantic images have class_name=normal.
Normal anomaly list paths use the `./images/...` convention, relative to their
list file's folder. Strong lists can replace the corresponding detector YAML
split paths to evaluate actual localization separately from weak supervision.

Each selected AITEX tile is emitted once, plus positive train-only copies;
other sources still emit each original once. Semantic positive
augmentation quota is min(3, ceil(max_training_class_frequency / class_frequency)),
taking the largest quota when an image has several classes. Non-AITEX semantic
normals get one copy; sampled AITEX backgrounds get none. ZJU train normals get one copy; defective ZJU images are not
augmented, keeping the autoencoder's normal-only training path separate.
Copies use flip p=0.5, brightness/contrast limits +/-0.12 with p=0.8 and rotation
up to +/-5 degrees with p=0.7. Bboxes and masks transform with their image.
This helps sample imbalance but does not create independent rare-class evidence.

Verification decodes every output image, checks all labels/masks and file pairs,
checks that each selected AITEX tile (and each other source image) appears once
before augmentation, verifies AITEX crop coordinates against source masks and
complete positive-mask coverage, checks parent and
decoded-source hash split isolation, and asserts no held-out augmentation.
Mask foreground must remain covered by saved boxes (one-pixel raster tolerance).
Ultralytics independently scans every semantic example and loads tensors, plus
16 actual ZJU examples (8 positive/8 normal) per split; the complete ZJU file
validation is performed by the main verifier. No weights or training are needed.
The existing GitHub CI only tests backend/frontend; these AI tests currently run
locally and are not covered by its two jobs.

## Verified real-data baseline (before synthetic extension)

After AITEX-only tiling, the active dataset contains **156,371 images**: **96,940
unaugmented source images/selected tiles** plus **59,431 train-only copies**,
seed 42. The source audit still contains 96,885 original source images; tile
counts must not be confused with independent source strips. Archived pre-tiling
outputs are excluded. The complete post-tiling output recheck **passed for all
156,371 images**, including labels/masks, expected file pairs, selected-tile
accounting, source-mask coverage and split isolation. No erased positive masks,
cross-split parents or decoded-source hash overlap were found. AITEX now has
**zero subpixel-dimension boxes**; eight pre-existing TILDA subpixel boxes remain
flagged and unchanged because that source is outside this tiling task.

Both YAMLs passed actual Ultralytics loading: all 4,635 semantic images and
4,289 boxes were accepted; 16 binary ZJU examples per split also loaded without
rejection or box loss. All ZJU outputs were independently checked by the full
verifier. Twelve regression tests, Ruff, Black --check and AI pip check passed.
No dependencies were added, no model trained, and no commit or push made.

Recorded manifest SHA-256 values (manifest contents, not image payload digests):

- output: `7a76dd4dc39001abaebe1af3eb33cfbad515696ae5a26e252b12a883aea9c961`
- source: `f506875447ad41fe8c7f6539a2677c25baae67ec8bfbd7fa7b3e9d78671bf373`

Runtime for this run: Python 3.12.14, Albumentations 2.0.8, headless OpenCV
5.0.0.93, NumPy 2.5.2, Pillow 12.3.0, Ultralytics headless distribution 8.4.133,
PyTorch 2.13.0 and PyYAML 6.0.3 (full metadata in verification.json).

| Track | Train | Validation | Test | Total |
|---|---:|---:|---:|---:|
| Semantic YOLO (includes normal backgrounds) | 4,217 | 210 | 208 | 4,635 |
| ZJU binary anomaly | 132,766 | 9,484 | 9,484 | 151,734 |
| AITEX classification-only | 2 | 0 | 0 | 2 |
| All outputs | 136,985 | 9,694 | 9,692 | 156,371 |

Semantic image distribution (not box counts; excludes classification-only):

| Class | Train | Validation | Test | Total |
|---|---:|---:|---:|---:|
| hole | 915 | 38 | 38 | 991 |
| weave_error | 1,132 | 68 | 68 | 1,268 |
| stain | 320 | 10 | 10 | 340 |
| foreign_object | 328 | 10 | 10 | 348 |
| crease | 24 | 2 | 2 | 28 |
| edge_damage | 36 | 2 | 1 | 39 |
| pattern_break | 464 | 15 | 15 | 494 |
| normal (empty detection label) | 998 | 65 | 64 | 1,127 |
| aitex_unmapped / tilda_unmapped | 0 | 0 | 0 | 0 |

The two extra classification-only positives are weave_error. Per-source final
outputs: rmshashi 1,425; AITEX 530 (528 detector + 2 classification-only);
TILDA 1,120; MVTec carpet/grid 1,562; ZJU 151,734. Semantic unaugmented inputs split
1,687/210/208 unaugmented images/tiles, plus two classification-only train originals;
semantic train augmentations total 2,530. ZJU originals split 75,865/9,484/9,484, with 56,901
normal-only train augmentations. ZJU positive counts are 18,964/2,371/2,371;
normal counts are 113,802/7,113/7,113.

TILDA repair expanded 245 supplied boxes, added two uncovered mask components,
and preserved one supplied box without mask overlap: 514 source boxes become
516 reconciled original boxes. Generated semantic box counts are
3,952/173/164; ZJU box counts are 28,728/3,452/3,495. Exact per-class box counts,
all file paths, exclusions, hashes and environment versions are recorded in
`verification.json` and the two JSONL manifests.

### AITEX tiling counts

| AITEX selection | Train | Val | Test | Total |
|---|---:|---:|---:|---:|
| Candidate native tiles | 4,094 | 525 | 525 | 5,144 |
| Positive tiles retained | 194 | 25 | 22 | 241 |
| Pure backgrounds sampled | 48 | 6 | 5 | 59 |
| Empty tiles discarded | 3,852 | 494 | 498 | 4,844 |
| Positive augmented copies | 228 | 0 | 0 | 228 |
| Detection output images | 470 | 31 | 27 | 528 |
| Classification-only strips | 2 | 0 | 0 | 2 |

All 104 localized defective source strips contribute tiles. Of 141 normal
strips, 37 contribute sampled tiles and 104 contribute none (still audited).
Two other defective strips remain classification-only. Overlapping crops are
not counted as new independent source evidence. Two of the 228 augmented
copies used the no-rotation tile-edge fallback.

AITEX detection image classes including augmentation (no classification-only):

| Class | Train | Val | Test | Total |
|---|---:|---:|---:|---:|
| weave_error | 354 | 21 | 19 | 394 |
| edge_damage | 36 | 2 | 1 | 39 |
| crease | 24 | 2 | 2 | 28 |
| foreign_object | 8 | 0 | 0 | 8 |
| normal/background | 48 | 6 | 5 | 59 |

The other four sources' processing logic, quotas, split assignments and
155,841 image outputs were unchanged. The scoped rebuild verified matching
non-AITEX manifest records and image/label/mask file sizes and modification times
before/after; its combined fingerprint is stored in `aitex-tiling.json`.
The previous 464 AITEX outputs and associated manifests remain recoverable under
`processed/_aitex_rebuild_td4qntsj/previous/`, outside active training paths.

### Visual review and limits before training

Five seeded random positive originals per source were rendered and inspected
(25 examples, plus full-image/detail contact sheets). TILDA, MVTec and ZJU
overlays align with visible annotated defects after reconciliation. The five
new seeded AITEX tile examples and their detail crops show retained weave detail
and aligned boxes, including clipped tile-edge regions. Fine/low-contrast defects
still require model evaluation; correct coordinates are not measured accuracy.
The original full-strip review is superseded for AITEX. rmshashi boxes deliberately
cover the whole fabric image, not defect boundaries; the source also mixes dark
photographs with binary-looking processed renditions. These are domain/label
quality limitations, not strong localization evidence.

**Before training:** define a strong-label-only baseline and evaluate the tiled
AITEX input protocol without tuning on the final test split. Do not report weak-label scores as measured
localization accuracy, claim unseen-roll generalization from these image splits,
or treat augmentation as independent rare-class evidence. Crease and edge_damage
have only one original per held-out split. Pattern_break is a texture-anomaly
proxy, not a clean physical-defect class. No training, accuracy, latency, or
production-rights claim is made by this preprocessing result.

## Disclosed synthetic defect augmentation

`ai/preprocessing/synthetic_defects.py` implements a deliberate mitigation for
scarce crease and edge_damage labels, and an additional foreign_object variation
experiment. Synthetic labels describe the **inserted proxy**, not a newly
discovered real defect. These are procedural appearance approximations, not
textile-physics simulations, evidence of real-world accuracy, or independent
real defect observations. This strategy must be disclosed in the FYP report.

### Recipes and provenance

- **crease:** thin dark quadratic curved line with a soft shadow and adjacent
  light ridge, approximating a fold.
- **edge_damage:** jagged border cutaway with projecting fibers, randomized over
  all four image borders. A patch border is not a verified physical fabric
  selvage: this is an edge-appearance proxy and may teach border shortcuts.
- **foreign_object:** a small irregular contrasting debris patch or a curved
  stray thread with variable color/opacity/texture.

The exact changed-pixel support is saved as a binary insertion mask; its tight
rectangle produces the normalized YOLO box. Images are lossless PNGs so pixels
outside the insertion support remain exactly equal to the background. No label
text or watermark is embedded in training pixels. Only review montages are
visibly annotated `SYNTHETIC`.

Every generated filename starts with `synthetic_`. Each manifest row explicitly
has `synthetic: true`, `source: synthetic`, `annotation_kind: synthetic_mask`,
generator version, recipe parameters/seed/index, background filename/source/file
SHA-256, source parent ID/pixel hash and the original raw reference. Existing
rows without `synthetic` mean non-synthetic; some still have `augmented: true`
because of ordinary image transforms. Synthetic rows also set `augmented: true`
as derivatives; use the synthetic flag to distinguish these categories.

Only original, non-augmented, unpadded normal **training** backgrounds are
eligible. Default source is ZJU; optional sources are AITEX, MVTec or `all`.
No held-out parent/hash may be selected. Hash partitions and seed 42 select
distinct backgrounds across the three synthetic classes, and increasing quotas
preserves previously selected recipes. ZJU's native files and binary labels are
not edited; derived examples retain ZJU attribution and applicable license
restrictions, including the documented non-commercial academic scope.

### Initial quotas and honest class counts

Defaults target at least 200 total training images per requested class, with a
minimum of 50 synthetic examples per class to exercise every generator. Existing
foreign_object already has 328 training images, so its extra 50 are a disclosed
variation experiment, not a claim that it was below 200. Existing counts below
include ordinary augmentation/tiles and are **not independent real defect counts**.

| Class | Existing non-synthetic train images | Verified synthetic addition | Current total |
|---|---:|---:|---:|
| crease | 24 | 176 | 200 |
| edge_damage | 36 | 164 | 200 |
| foreign_object | 328 | 50 | 378 |

The verified extension adds **390 synthetic training images**. Current totals
are **156,761 outputs**: 5,025 semantic detector images (train/val/test
**4,607/210/208**), 151,734 unchanged ZJU anomaly images and two unchanged
classification-only positives. The 156,371 pre-existing outputs are unchanged:
96,940 unaugmented images/selected tiles plus 59,431 ordinary train augmentations.
Synthetic examples are additional derivatives, not additional independent sources.

`synthetic-verification.json` records exact recipe reproduction, mask/box support,
background provenance, unchanged real-file record/size/mtime fingerprints and
unchanged **file inventory plus SHA-256 contents of every val/test image, label
and mask** across both tracks and classification-only directories. Current
manifest SHA-256 is
`7fafc0c358d2e11fd1b5e134181f5d2586639ee7a9a4ee02cc07b478617db82e`.
The config's `real_manifest_sha256` fingerprints normalized non-synthetic JSONL
records, not the original manifest's platform-dependent newline bytes.

The earlier `verification.json` remains the full-decoding verification of the
**156,371-image real baseline**, not a new full-dataset decoding report. The
extension validates every new synthetic image/label/mask and preserves that
baseline; it does not repeat the full 151,734-image ZJU decode. Nine preview
examples (three per class) were visually inspected against their backgrounds
and annotated boxes; the final review sheet is
`_sanity_check/synthetic_contact.jpg`. These show insertion geometry, not
proven realism or improved accuracy. All 19 preprocessing regression tests,
Ruff, Black and the AI environment's dependency check pass.

The independent `--verify` rerun passed for all 390 synthetic examples; an
identical generation rerun reported **no files changed**. A separate manifest
audit confirmed identical real records, no cross-split parent/hash overlap and
exact semantic image/label/mask inventory. Ultralytics accepted **5,025 semantic
images and 4,679 boxes**, including all 390 new boxes, plus the existing bounded
16-image-per-split binary smoke check. Its valid held-out caches were reused;
this is loader compatibility, not a new full held-out decode or training run.
The foreign_object output contains 27 debris patches and 23 stray threads.

### Reproduce, configure and evaluate

From the repo root using the separate AI environment:

```powershell
.\ai\venv\Scripts\python.exe ai/preprocessing/synthetic_defects.py --preview
.\ai\venv\Scripts\python.exe ai/preprocessing/synthetic_defects.py
.\ai\venv\Scripts\python.exe ai/preprocessing/synthetic_defects.py --verify
# Absolute synthetic quotas, not extra copies on every invocation:
.\ai\venv\Scripts\python.exe ai/preprocessing/synthetic_defects.py --counts crease=200 edge_damage=200 foreign_object=75
```

`--target-train`, `--minimum-synthetic`, `--counts CLASS=N`, `--seed`,
`--background-source`, and `--output` are configurable. An identical rerun
verifies and makes no changes; quotas can grow without rewriting existing
samples. Decreasing quotas or changing the base/seed/generator code is refused:
build a separate real dataset and regenerate the extension there. The base
builder and source-refresh commands likewise refuse rebuilding underneath an
existing synthetic layer. Prior manifests are recoverably backed up under
ignored `_synthetic_stage_*/previous/`.

The standard `data.yaml` sees real plus synthetic images under `images/train`.
`real_train.txt` enables the non-synthetic baseline;
`strong_train.txt` remains real-only and also excludes weak rmshashi labels;
`synthetic_train.txt` lists only procedural examples. The classifier train
manifest includes synthetic flags. Val/test lists and images are not augmented
or changed. Compare a fixed real-only baseline against real-plus-synthetic
training on the **same real held-out sets**, report per-class metrics and
independent source counts, and disclose appearance/domain bias. No performance
benefit has yet been measured.
