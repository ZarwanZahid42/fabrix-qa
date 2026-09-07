# FabriX-QA Memory

> **Mandatory:** Every human or AI agent must read this file before starting any task.
> **Mandatory:** After every task, append/update this file and every affected living document.
> This is the single source of truth for what is actually built and decided. Target architecture is not implementation.

## Current state

| Field | Value |
|---|---|
| Date | 2026-09-05 |
| Branch observed | `features/zarwan` tracking `origin/features/zarwan` |
| Active stage | Foundation and targeted Phase 2 offline dataset preparation complete; Phase 1 product decisions remain open |
| Product implementation | Offline preprocessing and output verification complete; website/AI inference features not started |
| Next task | Define a real-only strong-label detector baseline and a disclosed real-plus-synthetic ablation on identical real held-out splits; remaining Requirements & Design decisions stay open |
| Team/product constraint | Two-person student team; website only; one FastAPI backend |

The repository contains a minimal buildable Next.js shell, a FastAPI health bootstrap with one real smoke test, local Docker Compose topology, pinned requirements, an offline dataset preprocessing pipeline with regression tests, purpose-only product-feature placeholders, and six living documentation files. It does **not** contain authentication, database models/migrations, inference, edge capture, scoring, grading, alerts, reports, dashboard features, or tests for those product features.

## What is built now

### Root and infrastructure

- `AGENTS.md` is the concise repository entry point for agents and directs them to Memory, Rules, and Phases as the policy source of truth.
- `.github/workflows/ci.yml` runs the exact `backend` and `frontend` jobs for pull requests targeting `main` or `dev`.
- The CI backend job uses Python 3.12 and runs Ruff, Black, and pytest; the frontend job uses Node.js 22 and runs npm install, lint, and build.
- `.gitignore` covers Python, Node/Next.js, environments, secrets, datasets, model weights, generated media/reports, database volumes, notebooks, editors, and logs.
- `.env.example` contains placeholders for application, JWT, PostgreSQL, MongoDB, Twilio, SMTP, frontend endpoints, all three model paths, inference thresholds, camera/ROI, physical fabric measurements, grade thresholds, and alert policy.
- `docker/docker-compose.yml` defines local frontend, backend, PostgreSQL, and MongoDB services and named volumes.
- PostgreSQL and MongoDB init files contain purpose comments only; no application schema is implemented.
- `README.md` explains scope, status, structure, setup, safety, workflow, and documentation.

### Frontend

- Next.js App Router shell with React, Tailwind CSS, and Recharts dependencies.
- Minimal root layout and landing page exist only to make the scaffold buildable.
- Planned dashboard/auth pages from the earlier scaffold remain non-functional placeholder views.
- Shared API/auth/WebSocket utility files are purpose-only comments.
- No Node.js backend, Socket.IO, state library, auth behavior, charts, or production UI is implemented.

### Backend

- FastAPI application bootstrap exposes only a basic health endpoint.
- `tests/test_health.py` boots the application with FastAPI TestClient and verifies `/health` returns HTTP 200 plus the exact service-status payload; this prevents pytest exit code 5 while preserving a useful smoke contract.
- The TestClient dependency is explicitly pinned as `httpx2==2.12.0`, verified for the currently resolved Starlette 1.6.0. Runtime verification confirms TestClient uses `httpx2`; `httpx==0.28.1` is also installed independently through FastAPI-Mail's requirements.
- `backend/venv` is a local Python 3.12.13 environment with the pinned backend requirements installed and `pip check` passing. It is ignored by Git.
- `app/api`, `core`, `models`, `schemas`, `services`, and `websockets` exist.
- All feature modules are purpose-only comments; there are no routers, models, schemas, services, database connections, JWT helpers, or WebSocket manager yet.
- Backend Dockerfile targets Python 3.12.

### AI and edge

- AI directories exist for datasets, notebooks, training, inference, models, and preprocessing.
- `ai/venv` is a separate local Python 3.12 environment with the complete pinned AI/CV stack installed and `pip check` passing. The 2026-09-05 run reports Python 3.12.14; prior setup verification reported 3.12.13. This task did not install or upgrade dependencies or runtimes. The environment is ignored by Git.
- The default Windows/PyPI install was verified as CPU-only: PyTorch `2.13.0+cpu`, torchvision `0.28.0+cpu`, `torch.version.cuda is None`, and CUDA is unavailable. OpenCV 5.0.0, Ultralytics 8.4.133, and Albumentations 2.0.8 import together.
- Training/inference modules and live ROI patch extraction remain placeholders. Offline `ai/preprocessing/build_dataset.py`, its tests, annotation inspection and Ultralytics load verification tools now exist.
- Edge stream and ROI files are purpose-only comments.
- Five local raw datasets contain 96,885 training candidate source images (plus two excluded TILDA reference images). The AITEX-tiled real baseline has 156,371 outputs. A disclosed, verified 390-image synthetic train-only extension now brings the active total to 156,761: 5,025 semantic detector images, 151,734 unchanged ZJU anomaly images and two classification-only positives. AITEX still has 530 outputs (528 detector tiles/copies plus two untiled classification-only strips). All raw/generated payloads and recoverable archives remain ignored by Git. No model weights, training runs, scoring logic or live frame processing exist.
- `ai/preprocessing/synthetic_defects.py` implements seeded crease, edge_damage and foreign_object appearance proxies using original normal training backgrounds, with exact support masks, YOLO boxes and explicit synthetic/background provenance. It can preview, generate, verify and grow configurable quotas without changing existing real data. Native ZJU remains anomaly-only; only explicitly tagged derivatives receive semantic labels from the procedural insertion.

### Documentation

- `PRD.md`: users, scope, requirements, non-functional goals, four-point distinction, acceptance, open decisions.
- `Architecture.md`: target boundaries, flows, data ownership, security, deployment, decisions, open architecture.
- `Rules.md`: mandatory Memory protocol, protected Git flow, standards, safety, data/AI/security rules.
- `Phases.md`: completed foundation plus the required five-phase checklist.
- `Design.md`: website-only role architecture, dashboard hierarchy, evidence presentation, design tokens, states, charts, accessibility.
- `Memory.md`: this real-state handoff.

## Decisions in force

| Date | Decision | Why |
|---|---|---|
| 2026-08-29 | FastAPI is the only backend; Next.js is the website layer | Matches the requested stack and keeps a two-person FYP maintainable |
| 2026-08-29 | PostgreSQL owns structured/audited state; MongoDB owns defect-media documents/metadata | Provides relational integrity while allowing flexible media metadata |
| 2026-08-29 | Use PyMongo's native async API, not Motor | Motor is deprecated; new code should use the supported async driver |
| 2026-08-29 | Use `ultralytics-opencv-headless` with one headless OpenCV wheel | Preserves Ultralytics/YOLO imports and avoids conflicting OpenCV packages in containers |
| 2026-08-29 | Python 3.12 and Node.js 22 are foundation baselines | Current compatible runtime baselines for pinned packages |
| 2026-08-29 | Use Argon2 through `pwdlib` when password auth is implemented | Modern adaptive password hashing without carrying legacy Passlib/bcrypt scaffold code |
| 2026-08-29 | Do not assume Redis, Celery, MLflow, Zustand, Axios, Socket.IO, ResNet-50, or Grad-CAM | These were not required; add/select only when a measured requirement or experiment justifies them |
| 2026-08-29 | Keep four-point score, A/B/C/D mapping, and yield-loss estimation separate | The four-point method does not define universal project grades or business loss |
| 2026-08-29 | Thresholds and standard-specific defect rules remain placeholders | They require a named standard/buyer specification and textile-domain validation |
| 2026-08-29 | Feature placeholders contain no logic; only minimal framework bootstraps run | The task is scaffold-only while CI/build smoke checks still need valid entry points |
| 2026-08-30 | Keep separate `backend/venv` and `ai/venv` environments | Backend web/test dependencies and the large AI/CV stack have different lifecycles and must not be mixed |
| 2026-09-03 | Restore `httpx2==2.12.0` for Starlette 1.6.0 TestClient | The original pin was correct; upstream documentation, installed source, and runtime verification confirm HTTPX2 is the intended adapter. The 2026-09-02 replacement was mistaken; FastAPI-Mail separately requires HTTPX |

## Dependency baselines

Pins were checked against official PyPI/npm metadata on 2026-08-29. On 2026-09-03, Starlette 1.6.0's version-specific PyPI documentation and installed source were checked to confirm the original `httpx2==2.12.0` TestClient pin. HTTPX version checks alone had not established which adapter Starlette intended. Key compatibility pairs are PyTorch 2.13.0 with torchvision 0.28.0, FastAPI 0.141.1 with Pydantic 2.13.5, and Next.js 16.3.3 with React 19.2.8. TypeScript is pinned to 6.0.3 because the current Next.js ESLint parser requires TypeScript below 6.1; the individually newer TypeScript 7.0.2 does not satisfy that peer constraint. ESLint is pinned to 9.39.5 because an eslint-config-next 16.3.3 transitive resolver still restricts ESLint to v9 even though the top-level config advertises ESLint 10 support. Full exact pins live in `backend/requirements.txt`, `ai/requirements.txt`, and `frontend/package.json`.

The AI environment uses the standard PyPI PyTorch distribution, which installed a CPU-only build on this Windows/Python 3.12 machine. CPU-only development needs no non-default command. GPU/CUDA installation must follow the official PyTorch selector for the evaluation machine and be recorded; do not assume the default installation provides GPU support.

## Open decisions / next work

Zarwan explicitly authorized offline dataset preparation ahead of completing the
remaining **Requirements & Design** decisions. That scoped task is now verified.
AITEX tiling is now implemented with fixed source-image split groups. The next AI
task is to define the real-only strong-label baseline and a controlled
real-plus-synthetic ablation, then measure the tiled inputs' model accuracy
without tuning on the final test split. Do not
treat overlapping tiles as independent evidence or weak full-frame labels as
precise localization ground truth. The following product decisions remain open:

1. Select/cite the actual four-point standard or buyer specification and validate size/point rules.
2. Define A/B/C/D and yield-loss policies with domain input.
3. Produce the complete role-permission matrix and user workflows.
4. Review the documented dataset limitations, missing source license/version records, and unseen-roll evaluation policy before model claims.
5. Choose evaluation hardware and measurable targets.
6. Finalize data contracts, schemas, state lifecycles, WebSocket envelope, and security/session model.
7. Create/test dashboard wireframes before implementing pages.

Do not start unrelated feature implementation merely because placeholder modules exist.

## Initial dataset preparation (2026-09-05, pre-tiling baseline)

The counts and AITEX full-strip limitations in this historical record describe
the initial build. The subsequent AITEX-only tiling entry below supersedes them;
the other four sources' processing is unchanged.

- The earlier blocked inspection did not write a manifest. This session resumed under explicit user rules permitting researched mappings, named fallback buckets, academic preprocessing despite missing bundled licenses, actual rmshashi folder labels, AITEX multi-mask OR/classification-only exceptions, and ZJU anomaly-only scope.
- **Resolved via documented dataset research:** AITEX code names come from the original Silvestre-Blanes et al. paper, Table 1. Project merges codes 002 broken_end, 006 broken_yarn, 010 broken_pick, 016 weft_curling, 019 fuzzy_ball, 025 warp_ball, 027 knots, 030 nep and 036 weft_crack into weave_error; 022 cut_selvage becomes edge_damage; 023 crease stays crease; 029 contamination becomes foreign_object. Research establishes the original names; broad merges are project decisions, not claims from the paper.
- **Resolved via documented dataset research:** TILDA-400 publisher IDs 0 hole, 1 foreign object/contamination, 2 oil stain, 3 thread-related defect map to hole, foreign_object, stain, weave_error. The publisher describes these names as an interpretation of original error codes, not an authoritative German class dictionary. Actual local input is 400 full-size 768x512 images, 100 per class, not 64x64 patches or a five-class normal-heavy dataset. Thus stain has 100 source examples.
- **User-resolved folder taxonomy:** rmshashi hole and captured/Hole merge into hole; horizontal, verticle and captured/Lines merge into weave_error. Normalize the source label verticle to vertical without renaming raw paths. No normal or stain source class exists. Full-image boxes are explicitly weak supervision. Captured/top-level overlap remains a caution, not an assumption of independence.
- **Track scope:** ZJU's 94,833 images are binary anomaly data only, excluded from semantic detector and classifier manifests. Normal-only train lists support future autoencoder training. MVTec carpet/grid subtypes all map to pattern_break as a coarse texture-anomaly proxy while preserving their actual subtype; this is not a claim that metal/glue/cuts are physically equivalent.
- **Unmapped/bucketed:** zero observed AITEX/TILDA samples. Stable IDs 7/8 reserve aitex_unmapped/tilda_unmapped for future unknown codes. Full source URLs, names, counts and rights evidence are in `ai/datasets/README.md`. Missing bundled rmshashi/AITEX/TILDA licenses are recorded gaps; proceed under Zarwan's explicit academic-use vetting, without asserting commercial rights or inventing download versions.
- Complete input audit decoded and hashed 96,885 images. It found 13 exact duplicate pairs, all rmshashi, with no label conflicts; duplicate groups share splits.
- Technical corrections: fixed the CLI's dataset-root path; OR-combined multiple AITEX masks for 0044_019_04 and 0097_030_03 before component extraction; treated the all-zero 0106_010_03 mask like known maskless 0100_025_08 (two weave_error classification-only positives, excluded from detection); clipped two TILDA decimal-rounding edge overshoots under 0.001 pixel.
- Visual review found truncated TILDA thread boxes and one plausible boundary-hole box absent from its mask. Reconciliation conservatively expands boxes to their linked mask regions, adds uncovered mask components using the sole image class, and retains unmasked supplied boxes. Raw annotations and their hashes are preserved.
- TILDA reconciliation expanded 245 boxes, added two uncovered components and preserved one supplied box without mask overlap. Its 514 original supplied boxes become 516 reconciled boxes, with originals and repair metadata retained.
- Full-output verification initially exposed 23 masks erased by nearest-neighbor downsampling. Area-occupancy downsampling now preserves thin positive masks, with a single-pixel regression test; the final complete recheck reports **zero erased masks**. Exact subpixel boxes are retained (89 boxes have a dimension below one pixel). This fixes annotation loss, not image-resolution loss. Ultralytics config-directory fallback was also corrected so tool caches stay under ignored processed/_toolcache.
- **Measured final outputs:** 156,305 images = 96,885 originals + 59,420 train-only augmented copies. Semantic detector train/val/test: 4,159/204/206; ZJU anomaly: 132,766/9,484/9,484; classification-only: 2/0/0. Generated artifacts occupy approximately 20.88 GB logical size (including masks, labels and manifests). Per-source totals: rmshashi 1,425; AITEX 464; TILDA 1,120; MVTec 1,562; ZJU 151,734. Per-class/per-split tables live in the dataset README and verification.json.
- Implemented `build_dataset.py`, nine regression tests, `inspect_annotations.py`, and `verify_ultralytics.py`. The builder preserves source hashes, coordinates, original labels, native split metadata and augmentation parent/seed lineage. Seed 42, source-image 80/10/10 with grouped decoded duplicates, and train-only augmentation. Custom splits replace native benchmark splits; no official benchmark or unseen-roll claim is justified.
- **Verification passed:** all 156,305 output images independently decoded; matching labels/masks, class ranges, nonempty positive splits, mask/box geometry, exact source accounting and no held-out augmentation checked. Zero cross-split parent or decoded-source hash overlap. Actual Ultralytics YOLOv8 architecture and both YAMLs load; its loader scans all 4,569 semantic images (4,006 boxes) plus 16 binary ZJU examples per split without image rejection or box loss, returning 3x640x640 tensors. The full ZJU population is covered by the independent verifier, not by the bounded loader smoke test.
- Visually inspected five seeded positive originals per source (25 total) and their contact sheets. TILDA/MVTec/ZJU boxes align with visible annotations. AITEX boxes align with source masks but defects often lose visible detail at 640x40 content resolution. rmshashi's weak boxes and mixed dark photos/binary-looking renditions require caution. Strong-label-only lists and classification/normal-only manifests are provided; no model training ran.
- Nine unit tests, Ruff, Black --check and AI pip check pass. No dependencies changed. Backend/frontend CI was not rerun or expanded: AI regression tests and dataset loading are local checks, not part of the existing two GitHub jobs. No remote CI/protection-state claim is made.
- Updated dataset README, Memory, Phases, Architecture, PRD and root README. Rules and Design were reviewed and remain applicable without changes. Only scoped dataset-audit/offline-preparation checkboxes are complete; missing license/version archival, stronger evaluation policy, live ROI, training and all remaining product work stay open. Remained on features/zarwan; raw/generated files are ignored and untracked; no staging, commits, pushes, protected branch or ruleset changes.

## AITEX-only tiling follow-up (2026-09-05)

- User requested AITEX-specific rebuilding without changing the other four sources. Read Memory/Rules/Phases and inspected the existing dirty feature worktree; preserved all previous session changes. No dependencies, taxonomy mappings, raw files, other-source conversion/augmentation logic, or split assignments changed.
- Use 256x256 native square crops at stride 192 (25% overlap), with a right-edge-anchored final crop where needed. Resize each crop to 640x640: native pixels scale by 2.5 rather than the old full-strip 0.15625, preserving 16 times the linear detail for 4096-wide strips without inventing new native resolution.
- OR original masks, crop them, and derive tight connected-component boxes in local tile coordinates before YOLO normalization. Retain every foreground-bearing tile, including clipped boundary defects and single-pixel regions. Independent checks compare saved labels/masks to the raw crop and verify full source-mask coverage.
- Fix source splits before tile selection. Tile IDs, parent IDs/pixel hashes, native crop windows, actual tile class, source class, transforms and augmentation seed/policy are recorded. All overlapping crops/copies inherit their parent split. Unknown-localization positives 0100_025_08 and 0106_010_03 remain whole-strip classification-only; their unknown defect positions cannot justify positive or negative tile labels.
- Sample at most floor(positive tiles / 4) background tiles per split, seeded and round-robin across eligible strips; no background augmentation. Candidates may come from normal strips or mask-empty regions of localized defective strips. Background output class is normal, not the defective parent's class. Discard remaining empty tiles explicitly; 104 normal strips contribute no selected tiles but remain audited.
- Actual selection: 5,144 candidates -> 241 positive tiles + 59 sampled backgrounds; 4,844 empty candidates discarded. Train/val/test positives 194/25/22; backgrounds 48/6/5. Positive train copies: 228. A boundary regression exposed rotation erasing a small edge defect; an AITEX-only deterministic flip/brightness fallback omits rotation when a labeled mask region is lost. Two actual copies used this fallback.
- **AITEX output counts:** 470/31/27 detector images across train/val/test = 528, plus two classification-only train strips = 530. Detector class totals: weave_error 394, edge_damage 39, crease 28, foreign_object 8, normal 59. Per-split tables and selection details are in `ai/datasets/README.md` and ignored `aitex-tiling.json`.
- **Combined active dataset:** 156,371 outputs = 96,940 unaugmented images/selected tiles + 59,431 train-only copies. Semantic detector splits 4,217/210/208; ZJU remains 132,766/9,484/9,484; classification-only remains 2/0/0. Source audit count stays 96,885; selected tile count is not an independent source-image count.
- `build_dataset.py --rebuild-aitex` stages and validates only AITEX, reuses existing source splits/augmentation quotas, checks raw-image/pixel/annotation hashes, and replaces only its generated files. Previous 464 AITEX outputs and associated manifests are recoverable in ignored `processed/_aitex_rebuild_td4qntsj/previous/`, outside active YOLO paths. No data was deleted. Before/after non-AITEX manifest records, file sizes and modification times matched for all 155,841 other-source output images and their labels/masks; the combined fingerprint is in `aitex-tiling.json` (this is not a full payload-content hash).
- AITEX staging and source-mask geometry verification passed for all 530 outputs: zero subpixel boxes and zero erased positive masks. Twelve regression tests pass, covering full strip/end coverage, clipped boxes, preserved tile-parent/split lineage, seeded repeatability, capped unaugmented normal selection and rotation fallback. Ruff, Black --check and AI pip check pass.
- Ultralytics loads the updated semantic YAML: all 4,635 images and 4,289 boxes accepted, with 640x640 tensors; binary ZJU loader smoke checks still pass. Five new seeded AITEX positives were visually inspected in `_sanity_check/aitex_contact.jpg`, with visible retained texture and boxes aligned to cropped annotations. The complete combined-output recheck **passed for all 156,371 images**, including labels/masks, expected file pairs, selected-tile accounting, source-mask coverage and split isolation. Zero erased positive masks or cross-split parent/decoded-source hash overlap. AITEX has zero subpixel boxes; eight pre-existing TILDA subpixel boxes remain flagged and unchanged, outside this task's scope.
- Updated dataset README, Memory, Phases and Architecture; the initial build entry is retained as explicitly historical. Current output-manifest SHA-256: `7a76dd4dc39001abaebe1af3eb33cfbad515696ae5a26e252b12a883aea9c961`; source-manifest SHA-256: `f506875447ad41fe8c7f6539a2677c25baae67ec8bfbd7fa7b3e9d78671bf373`. Final diff/ignore checks passed. Remained on `features/zarwan`; no staging, commit, push, branch-protection change, or model training. Raw/generated payloads and the previous-output archive are Git-ignored and untracked.
- Tiling is not a measured accuracy improvement. Overlap produces correlated samples; curated negative sampling changes prevalence; held-out rare classes still come from very few independent strips. Define the strong-label baseline, inference-time tiling/merge policy and source-level evaluation before training claims. Live ROI integration and trained models remain unimplemented. This task does not change backend/frontend CI or resolve manual GitHub required-check configuration.

## 2026-09-05 — Disclosed synthetic scarcity mitigation

- Implemented `synthetic_defects.py` under Zarwan's explicit authorization. This is a post-build extension, not a change to any raw dataset's processing logic. Creases use thin curved dark folds with ridge/shadow; edge_damage uses jagged/frayed border cutaways; foreign_object uses irregular contrasting debris or stray threads. These are procedural appearance proxies, not physical simulations or new real observations.
- Selected 390 distinct original, non-augmented, unpadded ZJU normal **training** backgrounds. Parent/source-pixel hashes cannot overlap held-out splits. Hash partitions, seed 42, generator version/code fingerprint and background SHA-256 make recipes reproducible and quota growth stable. Native ZJU images and binary labels remain unchanged; the permitted semantic exception is only the new tagged derivatives, whose class is defined by insertion.
- Added 176 crease, 164 edge_damage and 50 foreign_object images. Non-synthetic train counts were 24/36/328 respectively; combined counts are now **200/200/378**. Those existing counts include ordinary augmentation/tiles, not independent real defects. Foreign_object was already above 200: its 50 additions are a disclosed variation experiment, not a claim of an unmet numerical target.
- Current active outputs: **156,761 = 96,940 unaugmented images/selected tiles + 59,431 ordinary augmentations + 390 synthetic derivatives**. Semantic detector splits are **4,607/210/208** (5,025 total); ZJU anomaly remains **132,766/9,484/9,484**, classification-only **2/0/0**. Source audit remains 96,885. No synthetic sample enters val/test.
- Lossless PNG output, exact changed-pixel support masks and tight normalized YOLO boxes are generated together. Every image/label/mask basename starts `synthetic_`; manifest rows carry `synthetic: true`, `source: synthetic`, `annotation_kind: synthetic_mask`, seed/recipe/index, original parent/raw reference and background path/hash. Training pixels contain no text or watermark. The new synthetic-only manifest/list and real-only train list support explicit selection; `strong_train.txt` stays real-only. Classifier train metadata also carries synthetic flags.
- Default CLI targets 200 total train images with a minimum of 50 synthetic per requested class; per-class absolute quotas, seed/background source/output and preview/verify modes are configurable. Matching reruns verify without writes; quotas may grow, while decreases or changed base/recipe fingerprints are refused. Base build/refresh commands now refuse rebuilding underneath an existing synthetic layer; rebuild into a fresh output directory instead. Prior manifests are recoverable under ignored `processed/_synthetic_stage_c4ekr5e6/previous/`.
- Generation verified every synthetic output by seeded pixel-exact reproduction, unchanged pixels outside insertion support, matching masks/boxes and background provenance. Real records and all real payload size/mtime fingerprints matched before/after; every held-out image/label/mask's content SHA-256 and directory inventory also matched. Current manifest SHA-256: `7fafc0c358d2e11fd1b5e134181f5d2586639ee7a9a4ee02cc07b478617db82e`; source-manifest SHA-256 remains `f506875447ad41fe8c7f6539a2677c25baae67ec8bfbd7fa7b3e9d78671bf373`.
- Verification scope is explicit: `synthetic-verification.json` reports the new layer plus preservation checks. Existing `verification.json` is the earlier complete decode of the 156,371-image real baseline; the entire unchanged ZJU population was not decoded again in this task. Config `real_manifest_sha256` hashes normalized JSONL records rather than platform-specific line-ending bytes.
- All **19 preprocessing tests** pass, including train-only eligibility, held-out hash rejection, exact mask/box geometry, border placement, deterministic/disjoint recipes, idempotence, grow-only quotas, tamper rejection and rebuild guard. Ruff, Black (8 files) and AI `pip check` pass. Black used the documented writable local cache workaround; no dependencies changed. Nine examples (three per class) were visually inspected as background/generated/annotated comparisons.
- Follow-up validation passed: independent `--verify` checked all 390 synthetic outputs; identical default generation verified and reported no files changed. Manifest audit confirmed byte-hash-stable source manifest, identical real record values/order, zero cross-split parent/source-pixel hash overlap and exact semantic file inventory. Ultralytics accepted all **5,025 semantic images / 4,679 boxes** (train 4,607/4,342, val 210/173, test 208/164) and the existing 16-image-per-split anomaly smoke sample, with 3x640x640 tensors. Valid held-out loader caches were reused; this is not a fresh full decode or training run. Train selection lists contain 4,217 non-synthetic detector images, 2,924 strong real-only images, 390 synthetic images and 4,609 classifier rows (including two classification-only positives).
- Updated dataset README, Architecture, PRD and Phases to disclose provenance, the native-ZJU/derived-image distinction and limitations. Synthetic-dominant rare classes, appearance/domain bias, border shortcuts (image border is not verified fabric selvage), near-duplicate/roll-level uncertainty and only one real crease/edge_damage example per held-out split remain serious evaluation limitations. No training or accuracy benefit is claimed. Next: real-only baseline versus a controlled synthetic ablation, with identical real validation/test sets and transparent per-class reporting.
- Work stayed on `features/zarwan`; no commit, push, protected-branch or ruleset change. Generated data and backup manifests remain ignored. Existing backend/frontend CI does not exercise these offline AI tests; local validation is not a new GitHub CI result.

## Known issues and cautions

- GitHub branch-protection rulesets for `main` and `dev` still need to be updated manually in GitHub settings after this workflow is merged so that the exact `backend` and `frontend` checks are required. No ruleset settings were changed in this task.
- `frontend/package-lock.json` now captures the clean strict npm graph. Python direct requirements are exactly pinned, but a platform-specific transitive lock/constraints workflow remains a future tooling decision.
- ESLint 9.39.5 is already marked deprecated upstream, but `eslint-config-next` 16.3.3 currently has a transitive resolver that rejects ESLint 10. Re-evaluate this pin when Next.js updates that dependency.
- Frontend, backend, and AI dependencies are installed in their intended local environments. Docker images were not pulled; Docker Desktop's Linux daemon was not running during an attempted isolated Node 22 validation, so Node 22 was instead run directly through the downloaded `node@22` runtime.
- npm 11 emits a non-failing `allow-scripts` review notice for transitive package `unrs-resolver@1.12.2`; install, lint, and build still pass with zero reported vulnerabilities. Do not approve transitive install scripts without a separate supply-chain review.
- On this Codex desktop sandbox, Black's default user cache path is not writable and can stall `black.cache` import. Local validation succeeds by setting `BLACK_CACHE_DIR` to a writable temporary directory; GitHub Actions on Ubuntu is not affected.
- TestClient now uses the restored HTTPX2 pin without the deprecated HTTPX-fallback warning. Both distributions are expected in `backend/venv`: FastAPI-Mail 1.6.8 independently requires `httpx>=0.28.1`. Do not remove that transitive dependency to enforce HTTPX2-only installation.
- Docker Compose is a local-development scaffold, not production hardened.
- The applicable four-point standard, physical measurement method, grade thresholds, and yield-loss formula are unresolved and must not be fabricated.
- MongoDB media representation/retention and cross-store reconciliation are unresolved.
- Earlier 2024 scaffold code contained premature feature logic and undocumented dependencies. It was intentionally reset to placeholders on 2026-08-29; do not rely on its prior claims.

## Verification log

### 2026-08-29 foundation reconciliation

- Read the pre-existing Memory file before work.
- Confirmed the current feature branch and clean starting worktree.
- Queried official package registries for current pins and relevant compatibility constraints.
- Removed premature feature logic from backend, AI, edge, and shared frontend modules.
- Reconciled all six living documents to the real scaffold and requested scope.
- Confirmed all 35 required paths exist.
- Parsed frontend JSON configuration successfully.
- Compiled all backend, AI, and edge Python files with Python 3.12.13.
- Validated Docker Compose configuration with `.env.example`; Docker emitted only a host config-access warning and returned success.
- Resolved the complete backend requirements graph with pip on Python 3.12.
- Installed backend requirements in an isolated temporary virtual environment and passed a FastAPI `/health` smoke test; Starlette emitted a non-failing deprecation warning about the current TestClient/httpx adapter.
- Resolved the complete AI requirements graph with pip on Python 3.12, including torch 2.13.0 + torchvision 0.28.0 and the single headless OpenCV path. The large wheels were not installed.
- Generated `frontend/package-lock.json` with strict peer-dependency resolution and installed 396 packages.
- Passed `npm run lint` with zero warnings/errors.
- Passed `npm run build`; Next.js compiled, type-checked, and statically generated all placeholder routes.
- Passed `git diff --check` after removing Markdown trailing whitespace.

### 2026-08-30 agent entry-point instructions

- Added root `AGENTS.md` with the required pre-task reading, Git-rule, and post-task Memory-update instructions.
- Kept `AGENTS.md` intentionally short and delegated all detailed policy to the living documents under `docs/`.
- Verified the file references the three required documents and passed `git diff --check`.

### 2026-08-30 pull-request CI workflow

- Added `.github/workflows/ci.yml` for pull requests targeting `main` or `dev` only.
- Added the exact `backend` job on Ubuntu/Python 3.12: install `backend/requirements.txt`, Ruff, Black check, and pytest.
- Originally added the `frontend` job on Ubuntu/Node.js 20; this runtime mismatch was corrected to Node.js 22 in the follow-up verification below.
- Kept job identifiers and display names exactly `backend` and `frontend` for future required-check selection.
- Verified Ruff, Black, pytest, and pytest-asyncio are pinned in `backend/requirements.txt`; verified the frontend `lint` and `build` scripts exist.
- Parsed the workflow as YAML and asserted its only trigger, target branches, job keys/names, runners, working directories, runtime versions, and command order.
- Ran the pinned backend CI tools locally: Ruff and Black passed; pytest initially collected zero tests and returned exit code 5. This blocker is resolved in the follow-up verification below.
- The frontend lint and production-build commands passed in the installed environment; exact Node 22 execution was verified in the follow-up below.
- Branch-protection/ruleset changes remain a manual GitHub settings action after merge and were not touched.

### 2026-08-30 CI fixes and isolated environments

- Added empty `backend/tests/__init__.py` and a maintainable `/health` smoke test using FastAPI TestClient. The test verifies application bootstrap, HTTP 200, and the exact `status`/`service` JSON contract.
- Correctly selected `httpx2==2.12.0` for Starlette TestClient after following its upstream migration warning. The 2026-09-02 session mistakenly reclassified this as an incorrect dependency; that assessment and replacement were reversed on 2026-09-03.
- Updated the frontend CI runtime from Node.js 20 to Node.js 22 to match `frontend/package.json`.
- Created and activated separate ignored Python 3.12.13 environments at `backend/venv` and `ai/venv`; installed each requirements file and passed `pip check` in both.
- Confirmed `.gitignore` rules for both `.venv/` and `venv/` exclude each environment; neither appears in Git status.
- Fully installed and import-tested the AI/CV stack. The default PyTorch/TorchVision wheels are CPU-only on this machine, so CPU-only setup needs no special install command. GPU/CUDA setup remains hardware-specific and must use the official PyTorch selector.
- Parsed `.github/workflows/ci.yml` successfully and asserted the `main`/`dev` PR targets, exact `backend`/`frontend` jobs, and Node.js 22 configuration.
- Passed backend Ruff, `black --check .` (27 files unchanged), and pytest (`1 passed`, no warnings). Passed frontend `npm install`, lint, TypeScript checks, and the optimized production build under Node.js 22.23.2.
- `npm install` reported zero vulnerabilities; npm 11 also emitted an informational install-script review notice for `unrs-resolver`, which did not block lint or build.
- Passed `git diff --check`; Git emitted only existing Windows LF-to-CRLF conversion notices.
- Branch-protection/ruleset configuration remains the one manual action after merge: require exact `backend` and `frontend` checks on `main` and `dev`. No GitHub settings were changed.

## Session history

### 2026-08-04 — Earlier scaffold (superseded where inconsistent)

An earlier scaffold created the main folders and broad placeholder set. Its Memory entry also claimed Redis/Celery/MLflow, ResNet-50, Grad-CAM, extra defect categories, database models, WebSocket management, and authentication helpers. Those choices exceeded the stated foundation scope or were actual premature logic.

### 2026-08-29 — Foundation rebuilt and documented

The scaffold was brought back to the requested website-only, one-FastAPI-backend scope. Dependencies were modernized, conflicting/deprecated choices removed, feature files converted to purpose-only placeholders, environment/infrastructure files corrected, and the living documentation rewritten with explicit open decisions and honest implementation status.

### 2026-08-30 — Root agent instructions added

Added a concise `AGENTS.md` entry point that requires agents to read Memory, Rules, and Phases, follow the documented Git workflow, and update Memory after every completed task.

### 2026-08-30 — Pull-request CI added

Added the `backend` and `frontend` GitHub Actions jobs for pull requests into `main` and `dev`, documented current first-run blockers, and left protected-branch rulesets unchanged for manual configuration after merge.

### 2026-08-30 — CI blockers fixed and Python environments installed

Added the real health smoke test, aligned CI with Node.js 22, installed separate backend and AI Python 3.12 environments, verified the CPU-only AI build, and passed the complete local CI-equivalent validation. The HTTPX2 direct pin selected in this session was correct for Starlette 1.6.0. It was mistakenly replaced on 2026-09-02 and restored on 2026-09-03. No commit, push, protected branch, or ruleset change was made.

### 2026-09-02 — Mistaken HTTPX replacement (superseded 2026-09-03)

- Manual `pip show`, PyPI, and `pip index versions` checks were performed, but their interpretation was wrong. HTTPX2 being a separate distribution with an empty `Required-by` field did not mean it was unrelated or unused: optional dependencies can be consumed without appearing there.
- HTTPX 0.28.1 was verified as the stable HTTPX release at the time, but that did not establish the correct dependency for this project's Starlette version.
- Mistakenly replaced `httpx2==2.12.0` with `httpx==0.28.1`, uninstalled HTTPX2 and its `httpcore2`/`truststore` dependencies from `backend/venv`, and reinstalled requirements. These were actual actions, not a valid correction; they were reversed on 2026-09-03.
- Ruff, Black, pytest (`1 passed`), and `pip check` passed using Starlette's deprecated HTTPX fallback. The observed deprecation warning explicitly recommended HTTPX2 and should have prompted correction of the diagnosis.
- The direct-requirement import/metadata audit found no other mismatch, but failed to interpret the version-specific optional TestClient dependency correctly.
- `ai/venv` was independently checked: `pip check` and core AI/CV imports passed, with HTTPX 0.28.1 through its own dependency graph and no HTTPX2.
- Retracted diagnosis: there was no original missing TestClient pin masked by FastAPI-Mail. Manual verification did not uncover an HTTPX2 defect, and CI had no such defect to catch; the agent incorrectly inferred one from metadata. The later fallback still passing did not justify replacing the original correct pin.
- Added dependency-identity verification guidance to Rules; that useful general policy was expanded on 2026-09-03 to require checking the consuming library's exact version, optional dependencies, and actual runtime adapter.
- Remained on `features/zarwan`; no commit, push, protected branch, or branch-protection/ruleset change was made.

### 2026-09-03 — Correct HTTPX2 pin restored and record amended

- Rechecked the [official Starlette 1.6.0 PyPI dependency section](https://pypi.org/project/starlette/1.6.0/#dependencies), which identifies HTTPX2 for TestClient. Installed Starlette source first imports `httpx2 as httpx`; standard HTTPX is only its deprecated fallback.
- Restored `httpx2==2.12.0` in `backend/requirements.txt`. The original pin was correct all along for the project's currently resolved Starlette 1.6.0; the previous replacement was an agent verification error.
- Uninstalled HTTPX from `backend/venv`, then reinstalled requirements using that environment's Python 3.12.13 interpreter. The sandbox initially blocked PyPI access; the network-enabled retry installed HTTPX2 2.12.0, HTTPCore2 2.12.0, Truststore 0.10.4, and HTTPX 0.28.1 successfully. HTTPX was correctly reintroduced by FastAPI-Mail 1.6.8's independent `httpx>=0.28.1` requirement.
- Asserted at runtime that `starlette.testclient.httpx is httpx2`, with version 2.12.0 loaded from `backend/venv`. TestClient no longer uses the transitive HTTPX fallback.
- Passed `python -m ruff check .`, `python -m black --check .` (27 files unchanged), pytest (`tests/test_health.py`: `1 passed`, no warnings), and `python -m pip check` (no broken requirements). Local Black and pytest caches were redirected to writable temporary directories because of sandbox cache permissions; no warnings were suppressed.
- Corrected the current-state summary, decision table, cautions, and historical misdiagnosis in this file. Amended Rules to preserve package verification while requiring evidence from the consuming framework's specific version and runtime imports.
- No product code, tests, frontend, AI environment, or CI workflow was changed. Phase completion is unchanged; the existing manual GitHub required-check configuration remains outstanding.
- Remained on `features/zarwan`; no commit, push, protected branch, or branch-protection/ruleset change was made.
