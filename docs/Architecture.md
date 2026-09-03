# FabriX-QA Architecture

**Version:** 1.0
**State:** Target architecture; only foundation scaffold exists
**Last updated:** 2026-08-29

## 1. Architectural principles

- One Python backend: FastAPI owns REST, native WebSockets, authentication, grading orchestration, alerts, and persistence. There is no Node.js API server.
- Edge processing is bounded and failure-aware; slow consumers must not grow memory without limit.
- The AI pipeline produces evidence and provenance, not only a label.
- PostgreSQL is the system of record for structured business state. MongoDB owns defect-media documents/metadata.
- Scoring rules, model versions, thresholds, and human corrections are versioned and auditable.
- The browser never connects directly to databases, cameras, Twilio, SMTP, or model files.
- Features are implemented phase by phase; this document describes intent, not completed behavior.

## 2. System context

```text
Camera / recorded video
        |
        v
Edge capture (OpenCV: source, timestamp, ROI, bounded frame buffer)
        |
        v
AI/CV pipeline
  YOLOv8 detector -> CNN classifier -> heatmap
          \------ autoencoder anomaly signal ------/
        |
        v
FastAPI application (single backend)
  REST + native WebSocket + JWT RBAC
  grading + yield + alerts + reporting orchestration
        |                    |                    |
        v                    v                    v
 PostgreSQL             MongoDB            Twilio / SMTP
 structured truth       media metadata      external alerts
        \____________________|____________________/
                             |
                             v
              Next.js website dashboard
               Tailwind CSS + Recharts
```

The edge and AI modules may initially run in the same Python process/environment for the two-person FYP. A process/service split is allowed later only if measurements show it is necessary and the change is documented.

## 3. Repository boundaries

| Path | Responsibility | Foundation state |
|---|---|---|
| `frontend/` | Next.js website, Tailwind styling, Recharts views, browser WebSocket client | Minimal buildable shell only |
| `backend/app/api/` | Versioned REST routers | Purpose-only placeholders |
| `backend/app/core/` | Settings, persistence lifecycle, JWT/RBAC primitives | Purpose-only placeholders |
| `backend/app/models/` | PostgreSQL ORM models | Purpose-only placeholders |
| `backend/app/schemas/` | Pydantic boundary contracts | Purpose-only placeholders |
| `backend/app/services/` | Grading, yield, notifications, reports | Purpose-only placeholders |
| `backend/app/websockets/` | Authenticated live-event connections | Purpose-only placeholders |
| `ai/datasets/` | Dataset instructions/manifests; raw data is ignored | Documentation only |
| `ai/training/` | Reproducible model training entry points | Purpose-only placeholders |
| `ai/inference/` | Unified inference and heatmap generation | Purpose-only placeholders |
| `ai/models/` | Model documentation; weights are ignored | Documentation only |
| `ai/preprocessing/` | Data/ROI transformations and augmentation | Purpose-only placeholders |
| `edge/` | Camera streaming and ROI selection | Purpose-only placeholders |
| `docker/` | Local Compose topology and database init hooks | Infrastructure scaffold |
| `docs/` | Living product, architecture, rules, phases, design, memory | Initial baseline |

## 4. Runtime responsibilities

### 4.1 Edge capture

`stream_handler.py` will own source lifecycle, timestamps, frame sequence numbers, reconnect behavior, sampling, and a bounded handoff buffer. `roi_selector.py` will validate and persist ROI coordinates independent of display resolution. Raw video should not traverse FastAPI unless a later measured design requires it.

### 4.2 AI/CV pipeline

A frame contract should contain frame ID, capture time, line/camera/roll IDs, ROI transform, and image array. The inference result should contain:

- detector boxes, class-agnostic objectness/confidence, and inference time;
- CNN class probabilities for hole, stain, weave error, and pattern break;
- autoencoder anomaly score and calibration version;
- accepted/rejected fusion decision and reason;
- heatmap/media references;
- model names, weight hashes/versions, preprocessing version, and device.

The CNN architecture, heatmap technique, and fusion rule remain open until dataset experiments. Training and inference transforms must share a versioned contract.

### 4.3 FastAPI backend

Planned logical layers:

```text
API/WebSocket adapters
        |
Pydantic contracts + JWT/RBAC dependencies
        |
Application services (inspection, grading, alerts, reports)
        |
Persistence adapters (SQLAlchemy/asyncpg, PyMongo Async API)
        |
PostgreSQL and MongoDB
```

Route handlers should translate protocols, not contain grading or model logic. WebSocket messages require explicit event names and schema versions. Background alert delivery must not block the frame/inference path; the concrete in-process/background mechanism is deferred and no Redis/Celery dependency is assumed.

### 4.4 Next.js website

The App Router website consumes REST for queries/commands and native WebSocket events for live updates. Backend authorization is authoritative; client-side role checks exist only for navigation and user experience. Recharts receives aggregated/time-series payloads rather than raw database data.

## 5. Data ownership

### PostgreSQL: structured system of record

Planned concepts include users, roles, production lines, cameras, fabric rolls, inspections, defect events, four-point rule sets, score contributions, roll grades, grade corrections, alerts, notification attempts, report jobs, and audit events. Exact tables and migrations are designed in the integration phase.

### MongoDB: defect-media documents

A media document should link to a PostgreSQL defect-event ID and include capture timestamp, media kind, dimensions, encoding/storage reference, heatmap metadata, model provenance, and retention state. Cross-database operations cannot be atomic; the service must use stable IDs, idempotent writes, and reconciliation for partial failure.

Binary storage versus filesystem/object reference is deliberately unresolved. Base64-in-JSON is not the default because of size overhead.

## 6. Event and data flow

### Accepted defect

1. Edge captures, timestamps, crops ROI, and submits a frame.
2. AI returns detection/class/anomaly evidence and heatmap output.
3. Backend validates the event and assigns stable IDs.
4. Structured event/provenance is persisted in PostgreSQL.
5. Media metadata/document is persisted in MongoDB with the same stable reference.
6. Four-point aggregation updates the active roll using a versioned rule set.
7. An authorized WebSocket event is broadcast.
8. If policy triggers, notification attempts are queued and their outcomes recorded.

Idempotency keys based on line/camera/roll/frame/detection identity must prevent duplicate persistence after retries.

### Roll completion

1. Freeze the inspected length/width and rule-set version.
2. Validate coverage and unresolved persistence errors.
3. Sum score contributions and normalize to points per 100 square yards.
4. Map the score to configured A/B/C/D grade and calculate yield loss.
5. Persist the immutable computed result.
6. Broadcast the grade event and make the roll available to reports.
7. Any later correction creates an audit record rather than erasing the original.

## 7. Security architecture

- Short-lived signed JWT access tokens with role and subject claims; refresh/session design is deferred.
- Passwords hashed with Argon2 through `pwdlib`.
- Deny-by-default FastAPI dependencies for role-protected operations.
- WebSocket authentication at connection time plus authorization by line/scope.
- Secrets loaded from environment and excluded from source control.
- CORS restricted to configured website origins.
- Input limits for uploads/messages and safe media content types.
- Audit events for authentication, policy changes, grade corrections, user changes, and exports.
- TLS and reverse proxy are deployment-phase concerns, not implemented in the scaffold.

## 8. Deployment topology

The local scaffold uses Docker Compose for Next.js, FastAPI, PostgreSQL, and MongoDB. Model training is not part of the web Compose path and may require a separate CUDA-enabled environment. Production hardening will add immutable frontend images, non-root containers, health/readiness checks, backups, secret management, TLS termination, resource limits, and documented restore procedures.

## 9. Technology decisions

| Decision | Rationale |
|---|---|
| FastAPI as the only backend | Native async REST/WebSocket support and a coherent two-person-team architecture |
| Next.js website only | Meets dashboard/reporting needs without mobile scope |
| PostgreSQL + MongoDB | Separates relational/audited business data from flexible media metadata |
| PyMongo Async API, not Motor | Motor is deprecated; avoids beginning new work on a retiring driver |
| `ultralytics-opencv-headless` | Retains Ultralytics imports while avoiding duplicate GUI/headless OpenCV wheels in containers |
| Python 3.12 / Node 22 baseline | Current supported runtimes with broad package compatibility |
| No Redis/Celery in foundation | Not required by the stated stack; add only if measured delivery/reliability needs justify it |

## 10. Open architecture decisions

- In-process versus separate edge/AI runtime after performance measurement.
- Internal event queue/backpressure strategy.
- Media bytes versus managed file/object references and cleanup process.
- JWT refresh/revocation model.
- Four-point specification, grade mapping, and yield-loss formula.
- CNN architecture, heatmap method, and fusion calibration.
- WebSocket event envelope/versioning.
- Notification retry, cooldown, and dead-letter behavior.
