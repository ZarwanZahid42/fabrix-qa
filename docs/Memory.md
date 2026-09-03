# FabriX-QA Memory

> **Mandatory:** Every human or AI agent must read this file before starting any task.
> **Mandatory:** After every task, append/update this file and every affected living document.
> This is the single source of truth for what is actually built and decided. Target architecture is not implementation.

## Current state

| Field | Value |
|---|---|
| Date | 2026-09-03 |
| Branch observed | `features/zarwan` tracking `origin/features/zarwan` |
| Active stage | Foundation scaffold complete |
| Product implementation | Not started |
| Next phase | Requirements & Design |
| Team/product constraint | Two-person student team; website only; one FastAPI backend |

The repository contains a minimal buildable Next.js shell, a FastAPI health bootstrap with one real smoke test, local Docker Compose topology, pinned requirements, purpose-only feature placeholders, and the six living documentation files. It does **not** contain authentication, database models/migrations, inference, edge capture, scoring, grading, alerts, reports, dashboard features, or tests for those product features.

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
- `ai/venv` is a separate local Python 3.12.13 environment with the complete pinned AI/CV stack installed and `pip check` passing. It is ignored by Git.
- The default Windows/PyPI install was verified as CPU-only: PyTorch `2.13.0+cpu`, torchvision `0.28.0+cpu`, `torch.version.cuda is None`, and CUDA is unavailable. OpenCV 5.0.0, Ultralytics 8.4.133, and Albumentations 2.0.8 import together.
- Training/inference/preprocessing Python files are purpose-only comments.
- Edge stream and ROI files are purpose-only comments.
- No datasets, weights, training runs, model architectures, scoring logic, or frame processing exists.

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

The next task should remain in **Requirements & Design**:

1. Select/cite the actual four-point standard or buyer specification and validate size/point rules.
2. Define A/B/C/D and yield-loss policies with domain input.
3. Produce the complete role-permission matrix and user workflows.
4. Audit dataset licensing, labels, class balance, and leakage risk.
5. Choose evaluation hardware and measurable targets.
6. Finalize data contracts, schemas, state lifecycles, WebSocket envelope, and security/session model.
7. Create/test dashboard wireframes before implementing pages.

Do not start feature implementation merely because placeholder modules exist.

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
