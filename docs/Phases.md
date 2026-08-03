# FabriX-QA — Development Phases & Progress Tracker

> **Last Updated:** 2026-08-04  
> **Current Phase:** Phase 0 — Foundation (Scaffolding Complete)

---

## How to Use This File

- `[ ]` = Not started
- `[/]` = In progress
- `[x]` = Complete
- Update this file after every meaningful task completion.

---

## Phase 0 — Foundation & Setup
**Goal:** Project structure, tooling, documentation, and environment ready for development.

- [x] Define project scope and requirements (PRD.md)
- [x] Design system architecture (Architecture.md)
- [x] Create full folder/file scaffold
- [x] Generate backend requirements.txt with pinned versions
- [x] Generate AI requirements.txt with pinned versions
- [x] Create .gitignore (Python, Node, weights, datasets, env)
- [x] Create .env.example with all required variables
- [x] Create Docker Compose with Postgres, MongoDB, Redis services
- [x] Create DB init scripts (postgres/init.sql, mongo/init.js)
- [x] Write initial docs: PRD, Architecture, Rules, Phases, Design, Memory
- [ ] Initialize Git repository + first commit
- [ ] Configure pre-commit hooks (Black, Ruff, ESLint)
- [ ] Set up Alembic for database migrations

---

## Phase 1 — Authentication & User Management
**Goal:** Secure JWT-based RBAC fully operational. Users can log in with role-based access.

- [ ] Implement User SQLAlchemy model (PostgreSQL)
- [ ] Implement Alembic migration for users table
- [ ] Implement POST /auth/login endpoint with bcrypt verification
- [ ] Implement GET /auth/me endpoint
- [ ] Implement get_current_user FastAPI dependency
- [ ] Implement role-based access decorators (Operator / Maintenance / Manager)
- [ ] Create seed script for default admin user
- [ ] Build Login page (Next.js) with React Hook Form + Zod validation
- [ ] Implement JWT storage in httpOnly cookie
- [ ] Implement route guards on dashboard pages
- [ ] Test: Unit tests for security.py functions
- [ ] Test: Integration test for /auth/login happy path + invalid credentials

---

## Phase 2 — AI & Computer Vision Pipeline
**Goal:** YOLOv8 model trained and inference pipeline running on fabric images.

- [ ] Download and prepare AITEX dataset (see ai/datasets/README.md)
- [ ] Download and prepare NEU dataset
- [ ] Run patch extractor (preprocessing/patch_extractor.py)
- [ ] Define Albumentations augmentation pipeline (preprocessing/augmentation.py)
- [ ] Create data.yaml for YOLO training
- [ ] Train YOLOv8 baseline (training/train_yolo.py)
- [ ] Evaluate baseline: mAP@0.5, confusion matrix
- [ ] Log experiment to MLflow
- [ ] Implement DefectDetector class (inference/defect_detector.py)
- [ ] Train ResNet-50 classifier (training/train_classifier.py)
- [ ] Implement HeatmapGenerator Grad-CAM (inference/heatmap_generator.py)
- [ ] Train Autoencoder (training/train_autoencoder.py)
- [ ] Integration test: End-to-end frame → DetectionResult pipeline
- [ ] Save best model weights to ai/models/

---

## Phase 3 — Edge Integration & Real-Time Pipeline
**Goal:** Live camera frames flowing through AI pipeline and results persisted to databases.

- [ ] Implement StreamHandler (edge/stream_handler.py)
- [ ] Implement ROISelector with GUI + JSON persistence (edge/roi_selector.py)
- [ ] Implement asyncio Queue between edge → AI inference
- [ ] Implement DefectRecord persistence to PostgreSQL
- [ ] Implement defect image + heatmap storage to MongoDB
- [ ] Implement GradingEngine.compute_grade() (backend/services/grading_engine.py)
- [ ] Implement GradingEngine.compute_yield_loss()
- [ ] Implement automatic GradeRecord creation after inspection window
- [ ] Implement WebSocket ConnectionManager (backend/websockets/defect_stream.py)
- [ ] Wire AI output → WebSocket broadcast to frontend
- [ ] End-to-end test: Camera → AI → DB → WebSocket

---

## Phase 4 — Full-Stack Dashboard
**Goal:** Production-ready dashboard with live feed, analytics, alerts, and reports.

- [ ] Build Dashboard shell layout (sidebar, topbar, auth guard)
- [ ] Build Overview page: live defect event feed (WebSocket consumer)
- [ ] Build grade summary cards (A/B/C/D counts, trend)
- [ ] Build defect heatmap visualization overlay
- [ ] Build Reports page with Recharts: defect trend, grade distribution
- [ ] Build date-range picker for report filtering
- [ ] Implement PDF export (jsPDF or server-side)
- [ ] Implement CSV export
- [ ] Build Alerts page: alert log table + ack/dismiss
- [ ] Implement NotificationService: Twilio SMS
- [ ] Implement NotificationService: FastAPI-Mail email
- [ ] Build Settings page: threshold configuration
- [ ] Build User Management (Manager only): list/create/deactivate users
- [ ] Implement GET /grading/history with pagination
- [ ] Implement GET /reports/daily
- [ ] Implement GET /reports/export

---

## Phase 5 — Testing, Hardening & Optimization
**Goal:** System is stable, tested, performant, and deployment-ready.

- [ ] Backend: Achieve ≥ 70% test coverage on service layer
- [ ] Frontend: Lighthouse score ≥ 90 on dashboard pages
- [ ] AI: Model achieves ≥ 0.85 mAP@0.5 on test set
- [ ] Load test: System handles 25 FPS sustained frame throughput
- [ ] Security audit: Check all endpoints for missing auth guards
- [ ] Docker production build: multi-stage Dockerfiles
- [ ] Add nginx reverse proxy config
- [ ] Add HTTPS / TLS config
- [ ] Write final project documentation (separate from code docs)
- [ ] Record demo video
- [ ] Final FYP submission
