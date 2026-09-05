# FabriX-QA

FabriX-QA is a website-based final-year project for AI-assisted textile inspection. The planned system processes fabric video frame by frame, detects defects with YOLOv8, classifies holes/stains/weave errors/pattern breaks with a CNN, flags anomalies with an autoencoder, generates localization heatmaps, calculates an auditable four-point roll score and A/B/C/D grade, estimates yield loss, streams live evidence to a role-gated dashboard, and sends SMS/email alerts.

**Current status:** foundation scaffold plus offline dataset preprocessing. Product features and trained AI models are not implemented. See `docs/Memory.md` for verification status and `ai/datasets/README.md` for the real data inventory, mappings, build commands and limitations.

## Technology baseline

- Website: Next.js, React, Tailwind CSS, Recharts
- Backend: one FastAPI Python service with native WebSockets
- AI/CV: PyTorch, Ultralytics YOLOv8, OpenCV, Albumentations
- Data: PostgreSQL for structured/audited records; MongoDB for defect-media documents/metadata
- Security: JWT RBAC for Operator, Maintenance, and Manager
- Notifications: Twilio SMS and FastAPI-Mail email
- Deployment: Docker and Docker Compose
- Baseline runtimes: Python 3.12 and Node.js 22

There is no mobile app and no Node.js backend.

## Repository structure

```text
FabriX-QA/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── websockets/
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── ai/
│   ├── datasets/
│   ├── notebooks/
│   ├── training/
│   ├── inference/
│   ├── models/
│   ├── preprocessing/
│   └── requirements.txt
├── edge/
│   ├── stream_handler.py
│   └── roi_selector.py
├── docker/
│   ├── docker-compose.yml
│   ├── postgres/
│   └── mongo/
├── docs/
│   ├── PRD.md
│   ├── Architecture.md
│   ├── Rules.md
│   ├── Phases.md
│   ├── Design.md
│   └── Memory.md
├── .env.example
├── .gitignore
└── README.md
```

Some additional route/module placeholders keep planned boundaries explicit. They contain no feature behavior.

## Mandatory workflow for every session

1. Read `docs/Memory.md` before doing anything else.
2. Read the relevant living docs and inspect branch/worktree state.
3. Complete only the requested, phase-appropriate work.
4. Update `docs/Memory.md` and every affected living document.
5. Run and record relevant checks before stopping.

See `docs/Rules.md` for the binding Git, code, data, security, and AI rules.

## Local setup

### Prerequisites

- Git
- Python 3.12
- Node.js 22+
- Docker Engine with Docker Compose v2
- Optional CUDA-capable GPU for later AI experiments

### Environment

From the repository root:

```powershell
Copy-Item .env.example .env
```

Replace every `CHANGE_ME` value. Never commit `.env`.

### Frontend scaffold

```powershell
Set-Location frontend
npm ci
npm run lint
npm run build
npm run dev
```

The local website is served at `http://localhost:3000`.

### Backend scaffold

```powershell
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The health endpoint is `http://localhost:8000/health`. No product API exists yet.

### AI development environment

```powershell
Set-Location ai
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For GPU use, choose the correct PyTorch/CUDA installation for the exact evaluation machine and record it in Memory. Dataset files and model weights are intentionally ignored.

The preprocessing workflow builds separate multiclass YOLO and ZJU anomaly
datasets from five local sources. Its build/verification commands and academic
attribution references are in `ai/datasets/README.md`. ZJU is excluded from
multiclass training; normal-only and strong-localization manifests support the
corresponding training/evaluation paths. No training runs are performed by the
dataset builder.

### Docker Compose

After creating the root `.env`:

```powershell
docker compose -f docker/docker-compose.yml config
docker compose -f docker/docker-compose.yml up --build
```

Compose is for local development. It is not production hardened.

## Four-point grading warning

The four-point inspection score, the project's A/B/C/D mapping, and its yield-loss estimate are separate. Exact defect-size rules, units, grade thresholds, and loss assumptions must be selected from a named standard/buyer specification and validated with textile-domain input. Placeholder values must never be presented as real factory policy.

## Git workflow

```text
features/zarwan ─┐
                 ├─> dev ─> main
features/kaynat ─┘
```

Work only on the current feature branch. `dev` and `main` are protected: pull request, one approval, and passing CI are required. Never push directly or force-push them, and never change branch protection as part of feature work.

## Living documentation

| File | Purpose |
|---|---|
| `docs/PRD.md` | Product scope, requirements, success/acceptance, open product decisions |
| `docs/Architecture.md` | Target boundaries, data ownership, runtime flows, security, decisions |
| `docs/Rules.md` | Binding development, Git, documentation, AI/data, and security rules |
| `docs/Phases.md` | Foundation plus five implementation-phase checklists and exit gates |
| `docs/Design.md` | Website information architecture, evidence UI, states, charts, accessibility |
| `docs/Memory.md` | Authoritative current implementation state, decisions, issues, and history |

## Academic integrity and claims

Record dataset licenses, experimental splits, seeds, metrics, hardware, model/rule versions, and limitations. Do not report unmeasured accuracy, throughput, grading compliance, or production readiness. The project should be impressive because its evidence is reproducible and honest.
