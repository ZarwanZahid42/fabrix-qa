# FabriX-QA
### AI-Powered Fabric Defect Detection & Quality Grading System

> **Final Year Project** | Computer Science / AI Engineering  
> Built with Next.js · FastAPI · PyTorch · YOLOv8 · PostgreSQL · MongoDB

---

## Overview

FabriX-QA is an end-to-end quality control system for the textile industry. It uses computer vision (YOLOv8 + CNN classifier) to detect fabric defects in real-time from production-line cameras, automatically grades fabric rolls (A/B/C/D), calculates yield loss, and delivers instant alerts via SMS and email — all visualized on a live web dashboard.

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- CUDA-capable GPU (recommended for AI module)

### 1. Clone & Configure
```bash
git clone https://github.com/your-org/fabrix-qa.git
cd fabrix-qa
cp .env.example .env
# Edit .env with your real credentials
```

### 2. Start Infrastructure (Databases)
```bash
cd docker
docker-compose up -d postgres mongodb redis
```

### 3. Start Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4. Start Frontend
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000)

### 5. AI Module (Development)
```bash
cd ai
pip install -r requirements.txt
# See ai/datasets/README.md to download datasets
```

---

## Project Structure

```
FabriX-QA/
├── frontend/       # Next.js 14 dashboard (React + Tailwind + Recharts)
├── backend/        # FastAPI REST + WebSocket API
├── ai/             # PyTorch CV pipeline (YOLOv8, classifier, autoencoder)
├── edge/           # Frame ingestion, ROI selection
├── docker/         # Docker Compose + DB init scripts
└── docs/           # Living documentation (PRD, Architecture, Phases, etc.)
```

---

## Documentation

| Document | Purpose |
|---|---|
| [PRD.md](docs/PRD.md) | Product Requirements |
| [Architecture.md](docs/Architecture.md) | System Architecture & Data Flow |
| [Phases.md](docs/Phases.md) | Development Phases & Progress |
| [Design.md](docs/Design.md) | UI/UX Design Direction |
| [Rules.md](docs/Rules.md) | Coding Conventions & AI Agent Rules |
| [Memory.md](docs/Memory.md) | Living context log for AI coding sessions |

---

## Roles

| Role | Capabilities |
|---|---|
| **Operator** | View live dashboard, acknowledge alerts |
| **Maintenance** | All Operator capabilities + machine configuration |
| **Manager** | Full access: reports, grade overrides, user management |

---

## License
For academic use only — Final Year Project submission.
