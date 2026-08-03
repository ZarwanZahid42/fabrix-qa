# FabriX-QA — System Architecture

> **Version:** 1.0 — Initial Scaffold  
> **Last Updated:** 2026-08-04

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRODUCTION FLOOR                         │
│                                                                 │
│  [IP Camera / Webcam]                                           │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────┐                                            │
│  │   EDGE MODULE   │  stream_handler.py + roi_selector.py       │
│  │  (Frame Ingest) │  OpenCV VideoCapture → ROI crop            │
│  └────────┬────────┘                                            │
│           │ Raw frames (np.ndarray)                             │
└───────────┼─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         AI MODULE                               │
│                                                                 │
│  ┌──────────────┐    ┌─────────────────┐    ┌───────────────┐  │
│  │  YOLOv8      │───►│ CNN Classifier  │───►│ Heatmap Gen   │  │
│  │  Detector    │    │ (ResNet-50)     │    │ (Grad-CAM)    │  │
│  └──────────────┘    └─────────────────┘    └───────┬───────┘  │
│         │                    │                       │           │
│   detections           defect_type              heatmap_png     │
│         └──────────────────►▼◄──────────────────────┘          │
│                    ┌────────────────┐                           │
│                    │ Inference Out  │ DefectEvent JSON           │
│                    └───────┬────────┘                           │
└────────────────────────────┼────────────────────────────────────┘
                             │
            ┌────────────────┼──────────────────┐
            │                │                  │
            ▼                ▼                  ▼
     ┌─────────────┐  ┌────────────┐   ┌──────────────┐
     │  MongoDB    │  │  FastAPI   │   │  PostgreSQL  │
     │  (Images +  │  │  Backend   │   │  (Grades,    │
     │  Heatmaps)  │  │  (REST +   │   │  Users,      │
     └─────────────┘  │  WebSocket)│   │  Alerts)     │
                      └─────┬──────┘   └──────────────┘
                            │
                   WebSocket │ REST API
                            │
                      ┌─────▼──────┐
                      │  Next.js   │
                      │  Frontend  │
                      │ Dashboard  │
                      └────────────┘
                            │
                   ┌────────┴────────┐
                   │                 │
              ┌────▼───┐       ┌─────▼────┐
              │ Twilio │       │  Email   │
              │  SMS   │       │  SMTP    │
              └────────┘       └──────────┘
```

---

## 2. Component Descriptions

### 2.1 Edge Module
- **Technology:** Python, OpenCV
- **Location:** `/edge/`
- **Responsibilities:**
  - Connect to camera streams (USB webcam or RTSP IP camera)
  - Apply Region of Interest (ROI) crop
  - Forward frames to AI module via asyncio Queue or shared memory
- **Key Files:** `stream_handler.py`, `roi_selector.py`

### 2.2 AI Module
- **Technology:** PyTorch, Ultralytics YOLOv8, OpenCV, Albumentations
- **Location:** `/ai/`
- **Pipeline:**
  1. Frame enters `DefectDetector.predict(frame)` → YOLOv8 bounding boxes
  2. Each detected crop passed to ResNet-50 classifier → defect type label
  3. Grad-CAM heatmap generated for each crop → PNG bytes
  4. `DefectEvent` emitted: `{bbox, class_name, confidence, severity, heatmap_b64}`

### 2.3 FastAPI Backend
- **Technology:** FastAPI, SQLAlchemy (async), Motor (async MongoDB), Redis, Celery
- **Location:** `/backend/`
- **Responsibilities:**
  - REST API for all CRUD operations
  - WebSocket server for live defect event streaming to frontend
  - Grading engine (aggregates events → grade record)
  - Notification dispatch (Twilio + email)
  - JWT-based RBAC

### 2.4 Frontend Dashboard
- **Technology:** Next.js 14, React, Tailwind CSS, Recharts, Zustand
- **Location:** `/frontend/`
- **Responsibilities:**
  - Live defect feed (via WebSocket)
  - Grade summary + trend charts
  - Alert management
  - Report export
  - User management (Manager role)

---

## 3. Data Flow

### 3.1 Real-Time Defect Detection Flow
```
Camera Frame
  → Edge (ROI crop)
  → AI (YOLOv8 detect → classify → heatmap)
  → Backend (save DefectRecord to PostgreSQL, save image to MongoDB)
  → WebSocket broadcast to all connected dashboard clients
  → [If threshold exceeded] → Notification Service → Twilio SMS + Email
```

### 3.2 Grade Computation Flow
```
Every N seconds (configurable inspection window):
  → Backend reads DefectRecords for current roll
  → GradingEngine.compute_grade(defects, fabric_area)
  → Saves GradeRecord to PostgreSQL
  → WebSocket pushes grade_update event to dashboard
```

### 3.3 Authentication Flow
```
User submits credentials
  → POST /auth/login
  → Backend verifies password (bcrypt)
  → Returns signed JWT (role embedded in payload)
  → Client stores JWT in httpOnly cookie
  → All subsequent requests include Authorization: Bearer <token>
  → Backend decodes JWT, checks role for protected endpoints
```

---

## 4. Database Schema (Outline)

### 4.1 PostgreSQL (Structured)

#### `users`
| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| username | VARCHAR(50) | UNIQUE |
| email | VARCHAR(120) | UNIQUE |
| hashed_password | VARCHAR(255) | bcrypt |
| role | ENUM | operator / maintenance / manager |
| is_active | BOOLEAN | |
| created_at | TIMESTAMPTZ | |

#### `defect_records`
| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| timestamp | TIMESTAMPTZ | Indexed |
| production_line_id | INTEGER | FK (future) |
| defect_type | VARCHAR(100) | hole, stain, etc. |
| severity | VARCHAR(20) | low/medium/high/critical |
| grade_impact | FLOAT | Penalty score |
| mongo_ref_id | VARCHAR(24) | MongoDB ObjectId |
| acknowledged | BOOLEAN | |
| acknowledged_by | INTEGER | FK to users.id |

#### `grade_records`
| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| timestamp | TIMESTAMPTZ | Indexed |
| production_line_id | INTEGER | |
| roll_id | VARCHAR(50) | |
| grade | CHAR(1) | A / B / C / D |
| total_defects | INTEGER | |
| defect_density | FLOAT | per m² |
| yield_loss_pct | FLOAT | |
| graded_by_ai | BOOLEAN | |
| override_by_user_id | INTEGER | FK to users.id |

### 4.2 MongoDB (Unstructured / Binary)

#### Collection: `defect_images`
```json
{
  "_id": ObjectId,
  "defect_record_id": 123,
  "timestamp": ISODate,
  "image_base64": "<base64 string of cropped defect frame>",
  "heatmap_base64": "<base64 string of Grad-CAM overlay PNG>",
  "metadata": {
    "defect_type": "hole",
    "confidence": 0.92,
    "bbox": [0.12, 0.34, 0.45, 0.67],
    "production_line_id": 1
  }
}
```

---

## 5. API Endpoints (Planned)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /auth/login | Public | JWT login |
| GET | /auth/me | All | Current user |
| GET | /grading/latest | All | Latest grade per line |
| GET | /grading/history | All | Paginated grade history |
| POST | /grading/manual | Manager | Grade override |
| GET | /alerts/ | All | Alert log |
| POST | /alerts/{id}/ack | Operator+ | Acknowledge alert |
| GET | /reports/daily | Maintenance+ | Daily report |
| GET | /reports/export | Manager | PDF/CSV export |
| WS | /ws/defects/{line_id} | All | Live defect stream |

---

## 6. Deployment Architecture

```
Single VM (Docker Compose)
├── nginx (reverse proxy, SSL termination)
├── fabrix_frontend (Next.js, port 3000)
├── fabrix_backend (FastAPI, port 8000)
├── fabrix_postgres (PostgreSQL, port 5432)
├── fabrix_mongo (MongoDB, port 27017)
└── fabrix_redis (Redis, port 6379)
```
