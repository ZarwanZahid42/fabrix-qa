# FabriX-QA — Memory Log (AI Session Context)

> **CRITICAL:** This file is the single source of truth for context handoff between AI coding sessions.
> Every AI agent starting work on this project MUST read this file first.
> Every AI agent completing work MUST update this file before stopping.

> **Format:** Append entries chronologically. Never delete or overwrite past entries.

---

## 📌 Current State Summary

**Phase:** 0 — Foundation  
**Status:** Scaffold complete. Ready to begin Phase 1 (Authentication).
**Last Updated:** 2026-08-04  
**Last Action:** Full project scaffold created

---

## 🗺 What Has Been Built

### 2026-08-04 — Session 1: Project Scaffolding

**Completed:**
- Full folder/file structure created for all modules:
  - `/frontend/` — Next.js 14 + Tailwind + Recharts boilerplate
  - `/backend/` — FastAPI app with all route/model/schema/service placeholders
  - `/ai/` — PyTorch/YOLOv8 training + inference + preprocessing placeholders
  - `/edge/` — Stream handler + ROI selector placeholders
  - `/docker/` — docker-compose.yml + Postgres/MongoDB init scripts
  - `/docs/` — All 6 living documentation files

**Key Files Created:**
- `backend/requirements.txt` — pinned stable versions for all backend deps
- `ai/requirements.txt` — pinned stable versions for all AI/CV deps
- `.gitignore` — covers Python, Node, model weights, datasets, .env
- `.env.example` — all environment variables with placeholder values
- `README.md` — project overview + quick start guide
- `docs/PRD.md` — product requirements, modules, success metrics
- `docs/Architecture.md` — system diagram, data flow, DB schema outline, API endpoints
- `docs/Rules.md` — coding conventions + AI agent rules
- `docs/Phases.md` — 5-phase development tracker with checkboxes
- `docs/Design.md` — color palette, typography, layout specs, animations
- `docs/Memory.md` — this file

**Decisions Made:**
1. **Tech stack confirmed:** Next.js 14 / FastAPI / PyTorch / YOLOv8 / PostgreSQL / MongoDB / Redis
2. **Auth strategy:** JWT stored in httpOnly cookie; role embedded in token payload
3. **Database split:** PostgreSQL for structured records (users, grades, defects); MongoDB for binary image/heatmap data
4. **Grading scale:** A / B / C / D based on defect density per m² thresholds (tunable)
5. **Defect taxonomy:** hole, stain, weave_error, tear, broken_thread, contamination
6. **AI pipeline:** YOLOv8 (primary detector) → ResNet-50 (classifier) → Grad-CAM (heatmap)
7. **Autoencoder:** Used as fallback for novel/unseen defect types
8. **Frontend state:** Zustand (global) + React Hook Form (forms) + SWR or apiClient (server state)
9. **Notifications:** Twilio SMS + FastAPI-Mail (email); threshold-based triggering
10. **Deployment target:** Single VM with Docker Compose

---

## ⏳ What Remains (Next Steps)

### Immediate — Phase 1 (Authentication)
- Initialize Git repository
- Configure pre-commit hooks (Black, Ruff, ESLint)
- Set up Alembic for database migrations
- Implement `/auth/login` endpoint with bcrypt verification
- Implement `get_current_user` FastAPI dependency
- Build Login page in Next.js
- Implement role-based route guards

### After Phase 1 — Phase 2 (AI/CV)
- Download AITEX + NEU datasets
- Run preprocessing pipeline
- Train YOLOv8 baseline
- Implement DefectDetector inference class

---

## 🐛 Known Issues / TODOs

- [ ] `frontend/package.json` — `@radix-ui/react-badge` was included but is not a real Radix package; replace with a custom badge component or use another library.
- [ ] `backend/app/core/config.py` — `REDIS_URL` variable not yet added to Settings class; add when Celery is wired up.
- [ ] `docker/docker-compose.yml` — No nginx service yet; add in Phase 5.
- [ ] `ai/requirements.txt` — PyTorch version `2.3.1` requires manual CUDA-specific install for GPU support. Standard pip install gives CPU-only. Add note to README for GPU setup.
- [ ] Alembic not yet initialized; run `alembic init migrations` inside `/backend` before Phase 1.

---

## 🔑 Key Architectural Decisions Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-08-04 | Use YOLOv8 as primary detector | Best balance of speed and accuracy for real-time FPS requirements; Ultralytics API is developer-friendly |
| 2026-08-04 | PostgreSQL for structured + MongoDB for images | Structured data benefits from ACID compliance; binary image blobs belong in document store |
| 2026-08-04 | JWT in httpOnly cookie (not localStorage) | Prevents XSS token theft; industry best practice |
| 2026-08-04 | Pydantic v2 + pydantic-settings | v2 is the current stable version; pydantic-settings replaces pydantic's removed Settings class |
| 2026-08-04 | Motor (async MongoDB driver) | Consistent with FastAPI's async architecture; avoids blocking |
| 2026-08-04 | Celery + Redis for background tasks | Notification sending and report generation should not block API responses |
| 2026-08-04 | Albumentations for augmentation | Industry-standard, fast, YOLO-compatible bbox augmentation support |

---

## 📎 Reference Links

- [Ultralytics YOLOv8 Docs](https://docs.ultralytics.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [AITEX Dataset](https://www.aitex.es/afid/)
- [NEU Surface Defect DB](http://faculty.neu.edu.cn/yunhyan/NEU_surface_defect_database.html)
- [Albumentations Docs](https://albumentations.ai/docs/)
- [Motor Async MongoDB](https://motor.readthedocs.io/)
- [Pydantic v2 Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
