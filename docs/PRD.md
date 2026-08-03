# FabriX-QA — Product Requirements Document (PRD)

> **Version:** 1.0 — Initial Scaffold  
> **Last Updated:** 2026-08-04  
> **Status:** 🟡 Draft — Active Development  
> **Owner:** FabriX-QA FYP Team

---

## 1. Problem Statement

The textile manufacturing industry relies heavily on manual quality inspection — a slow, inconsistent, and human-error-prone process. Inspectors visually scan meters of fabric for defects (holes, stains, weave errors, tears) under time pressure on fast-moving production lines. This leads to:

- **Inconsistent quality**: Inspector fatigue causes missed defects, especially after the first hour of a shift.
- **High rework costs**: Defective fabric discovered late in production causes expensive downstream waste.
- **No real-time feedback**: Supervisors have no live visibility into quality metrics — reports are end-of-shift.
- **Lack of traceability**: Without digital records, it's impossible to correlate machine settings with defect rates.

FabriX-QA solves this by replacing (or augmenting) human inspection with an AI-powered computer vision pipeline that detects defects in real time, grades fabric rolls automatically, and delivers instant alerts to the right people.

---

## 2. Target Users

| Role | Description | Primary Use Cases |
|---|---|---|
| **Operator** | Production line worker monitoring the system | View live defect feed, acknowledge alerts |
| **Maintenance Engineer** | Technician responsible for machine health | Configure camera ROI, manage thresholds, view machine fault logs |
| **Quality Manager** | Supervisor overseeing QA across all lines | View grade trends, export reports, override grades, manage users |

---

## 3. Core Modules

### Module 1 — Frame Ingestion & ROI Selection (Edge)
- Connect to IP/USB cameras via RTSP or OpenCV
- Operator selects Region of Interest (ROI) to focus on fabric only
- Frames are preprocessed (resize, normalize) and forwarded to AI pipeline

### Module 2 — Defect Detection & Classification (AI/CV)
- **Primary detector:** YOLOv8 — real-time bounding box detection of defects
- **Classifier:** ResNet-50 — categorizes detected defect patches into types:
  - `hole`, `stain`, `weave_error`, `tear`, `broken_thread`, `contamination`
- **Anomaly backup:** Convolutional autoencoder — detects novel/unseen defect types via reconstruction error
- **Heatmap:** Grad-CAM overlay on detected regions for operator interpretability

### Module 3 — Quality Grading Engine (Backend)
- Aggregates defect detections over a fabric roll inspection window
- Computes defect density (defects per m²)
- Assigns grade: **A** (excellent), **B** (good), **C** (acceptable), **D** (reject)
- Calculates yield loss percentage
- Stores grade record in PostgreSQL

### Module 4 — Live Dashboard (Frontend)
- Real-time defect event feed via WebSocket
- Grade summary cards per production line
- Defect heatmap visualization
- Historical analytics (trend charts — Recharts)
- Role-gated views

### Module 5 — Alerts & Notifications
- Threshold-based triggers: if defect density exceeds configurable limit → alert
- SMS via Twilio, Email via FastAPI-Mail
- In-app alert log with acknowledge/dismiss

### Module 6 — Reports & Analytics
- Daily/weekly PDF and CSV reports
- Yield loss trend charts
- Defect type distribution breakdown
- Export functionality for Quality Manager

---

## 4. Functional Requirements

| ID | Requirement | Priority | Module |
|---|---|---|---|
| FR-01 | System must detect defects in real-time at ≥ 15 FPS | Must Have | 1, 2 |
| FR-02 | Detect minimum 6 defect types with ≥ 85% mAP@0.5 | Must Have | 2 |
| FR-03 | Grade fabric rolls A/B/C/D within 2 seconds of roll completion | Must Have | 3 |
| FR-04 | Deliver SMS/email alert within 30 seconds of threshold breach | Must Have | 5 |
| FR-05 | Dashboard must update live within ≤ 2 seconds of detection | Must Have | 4 |
| FR-06 | Role-based access: Operators cannot access Manager reports | Must Have | 4, 6 |
| FR-07 | Store defect images + heatmaps with MongoDB metadata | Must Have | 2, 3 |
| FR-08 | Export daily report as PDF and CSV | Should Have | 6 |
| FR-09 | ROI selection via GUI with saveable presets | Should Have | 1 |
| FR-10 | Autoencoder fallback for novel defect detection | Should Have | 2 |
| FR-11 | MLflow experiment tracking for model training | Nice to Have | 2 |
| FR-12 | Multi-line support (≥ 2 production lines) | Nice to Have | All |

---

## 5. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Performance** | Inference latency ≤ 100ms per frame on GPU |
| **Availability** | System uptime ≥ 99% during production hours |
| **Scalability** | Architecture must support ≥ 4 production lines with minimal changes |
| **Security** | All API endpoints require JWT; passwords bcrypt-hashed; HTTPS in production |
| **Auditability** | All grade overrides must be logged with user ID and timestamp |
| **Portability** | Entire stack deployable via `docker-compose up` on a single VM |

---

## 6. Out of Scope (v1.0)

- Mobile application
- ERP / MES system integration
- Multi-tenancy (single factory deployment)
- Automated machine control (actuator feedback)

---

## 7. Success Metrics

| Metric | Target |
|---|---|
| Defect Detection mAP@0.5 | ≥ 0.85 on held-out test set |
| False Negative Rate | ≤ 10% for critical defects |
| Grade Classification Accuracy | ≥ 90% agreement with expert manual grader |
| Alert Delivery Time | ≤ 30 seconds end-to-end |
| Dashboard Latency | ≤ 2 seconds from detection to UI update |
| User Satisfaction (FYP evaluation) | ≥ 4.0/5.0 in usability assessment |
