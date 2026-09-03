# FabriX-QA Product Requirements Document

**Version:** 1.0
**Status:** Foundation approved; implementation not started
**Last updated:** 2026-08-29
**Team:** Two-person final-year-project team
**Product form:** Website only; no mobile application

## 1. Product vision

FabriX-QA is an AI-assisted textile quality-control system that turns continuous fabric video into traceable defect events, localized heatmaps, roll-level four-point scores, A/B/C/D quality grades, yield-loss estimates, real-time alerts, and management reports. It is intended to replace inconsistent manual-only inspection with repeatable evidence while keeping people responsible for review and operational decisions.

## 2. Problem and opportunity

Manual inspection is affected by fatigue, line speed, subjective judgement, and incomplete record keeping. Missed defects create rework, rejected deliveries, and material loss; late reporting prevents maintenance teams from responding while a fault is still producing damaged fabric. FabriX-QA creates a live, searchable quality record and shortens the feedback loop between inspection, operations, maintenance, and management.

## 3. Users and access

| Role | Primary goals | Allowed capabilities |
|---|---|---|
| Operator | Monitor one or more lines and react quickly | View live feed and current grades; inspect heatmaps; acknowledge assigned alerts |
| Maintenance | Diagnose recurring machine or process problems | Operator access plus defect/line trends, technical context, and permitted configuration |
| Manager | Control quality policy and review business impact | All reporting, roll history, yield loss, user/role administration, alert policy, and audited grade review |

RBAC is deny-by-default. Final endpoint and page permissions must be captured in a permission matrix before authentication is considered complete.

## 4. In-scope capabilities

### 4.1 Edge capture

- Read USB/IP camera or recorded-video sources frame by frame with OpenCV.
- Configure and persist a fabric region of interest (ROI).
- Timestamp and identify frames with production line, camera, roll, and sequence context.
- Apply bounded sampling/backpressure so inference cannot create an unbounded queue.

### 4.2 AI and computer vision

- Use YOLOv8 to detect candidate defect regions.
- Use a PyTorch CNN classifier to classify confirmed regions as holes, stains, weave errors, or pattern breaks.
- Use an autoencoder anomaly score to flag visually unusual regions that supervised classes may miss.
- Generate a localization heatmap for each accepted defect event.
- Return model version, confidence, bounding box, anomaly score, timing, and preprocessing metadata for reproducibility.
- Calibrate detector/classifier/anomaly fusion on validation data; the fusion rule and CNN architecture are intentionally not fixed during scaffolding.

### 4.3 Four-point scoring and roll grading

FabriX-QA will implement the textile four-point inspection method: a defect contributes one to four penalty points based on its measured size, with no single defect contributing more than four points. The normalized roll score is expressed as points per 100 square yards:

```text
points_per_100_sq_yd =
    total_penalty_points * 3,600
    / (inspected_length_yards * fabric_width_inches)
```

The exact size bands, treatment of holes/openings, edge defects, repeated defects, unit conversion, and acceptance thresholds must be verified against the standard or buyer specification selected by the team and approved by a textile-domain reviewer. A/B/C/D labels are a FabriX-QA business mapping over the normalized score; they are configurable and must not be presented as universal four-point-system thresholds.

- Aggregate penalty points by roll and inspection segment.
- Preserve every scoring input and rule-set version for auditability.
- Calculate A/B/C/D grade and yield-loss estimate.
- Allow only authorized, reasoned, auditable corrections; never silently overwrite an AI result.

### 4.4 Website dashboard

- Show live defect events and current line/roll status through native FastAPI WebSockets.
- Display defect crops and heatmaps with confidence and severity context.
- Plot grade, defect-type, defect-rate, and yield-loss trends using Recharts.
- Provide filterable roll history, alert history, and exportable reports.
- Gate routes, controls, and backend operations by Operator/Maintenance/Manager role.
- Support desktop and factory-monitor use. A mobile app and mobile-first workflow are out of scope.

### 4.5 Notifications

- Trigger policy-based SMS alerts through Twilio.
- Trigger policy-based email alerts through FastAPI-Mail.
- Deduplicate/cool down repeated alerts and record delivery state without blocking the inspection path.
- Never expose provider credentials to the browser.

## 5. Functional requirements

| ID | Requirement | Priority | Verification |
|---|---|---:|---|
| FR-001 | Ingest a configured camera/video source frame by frame | Must | Integration test with recorded fixture |
| FR-002 | Apply a persisted ROI before inference | Must | Unit and integration tests |
| FR-003 | Detect candidate defects with YOLOv8 | Must | Held-out dataset evaluation |
| FR-004 | Classify holes, stains, weave errors, and pattern breaks with a CNN | Must | Per-class metrics and confusion matrix |
| FR-005 | Produce an autoencoder anomaly score for unknown visual deviations | Must | Normal/abnormal validation distributions |
| FR-006 | Generate and retain a defect localization heatmap | Must | Artifact and metadata test |
| FR-007 | Calculate versioned four-point penalties and normalized roll score | Must | Golden calculation fixtures |
| FR-008 | Map score to configurable A/B/C/D grade | Must | Boundary tests |
| FR-009 | Calculate a documented yield-loss estimate | Must | Formula and boundary tests |
| FR-010 | Persist users, roles, rolls, grades, alerts, audit logs, and structured events in PostgreSQL | Must | Migration/integration tests |
| FR-011 | Persist defect-image and heatmap metadata/documents in MongoDB | Must | Integration and referential-consistency tests |
| FR-012 | Stream authorized live events to the website through WebSockets | Must | Authenticated WebSocket test |
| FR-013 | Enforce JWT RBAC in the backend and website | Must | Permission-matrix tests |
| FR-014 | Send policy-based SMS and email alerts and track outcomes | Must | Provider sandbox/fake tests |
| FR-015 | Show live feed, grade trends, defect trends, and reports | Must | End-to-end acceptance tests |
| FR-016 | Export manager-authorized quality reports | Should | Export content test |
| FR-017 | Record model, rule, user, and timestamp provenance for changes | Must | Audit-log test |

## 6. Non-functional requirements

| Category | Initial target |
|---|---|
| Detection quality | Targets are established after dataset audit; report precision, recall, F1, mAP@0.5, and mAP@0.5:0.95 per class |
| Real-time performance | Demonstrate stable end-to-end processing at the agreed line/camera FPS on named evaluation hardware |
| Live UI latency | Accepted defect visible on the dashboard within 2 seconds under the demo workload |
| Availability | Recover cleanly from camera, database, WebSocket, and notification-provider interruptions |
| Security | Hashed passwords, short-lived JWTs, least-privilege RBAC, server-side secrets, validation, and audit logs |
| Privacy | Retain only necessary imagery; define retention/deletion policy before production-like data is used |
| Accessibility | WCAG 2.2 AA target for keyboard access, focus, contrast, text alternatives, and non-color status cues |
| Maintainability | Typed boundaries, small modules, migrations, reproducible model/config versions, automated CI |
| Reproducibility | Record dataset version, split, seed, preprocessing, package versions, model weights, and evaluation hardware |

Performance and accuracy numbers must be measured and documented; no unmeasured target may be reported as achieved.

## 7. Data and reporting

Minimum traceability links are: factory/line → camera → roll → inspection segment → frame → defect event → media/heatmap → four-point contribution → roll grade → alert/report. PostgreSQL owns identifiers and structured business state. MongoDB stores defect-media documents and metadata referenced by stable IDs; the final image storage representation and retention policy remain open decisions.

Reports should answer: which rolls are at risk, which defects dominate, where/when rates changed, how grades trend, what yield may be lost, which alerts were acted on, and which model/rule versions produced the result.

## 8. Out of scope for v1

- Native or hybrid mobile application.
- Automatic loom/machine actuation or emergency stopping.
- ERP/MES integration, multi-tenant SaaS, billing, or public customer portal.
- Claims of production certification before expert review and controlled validation.
- Training foundation models from scratch.

## 9. Acceptance definition

The FYP is acceptable when a reproducible demo processes representative fabric video, localizes and classifies the four required defect categories, surfaces anomaly evidence, calculates auditable four-point scores and grades, persists both database views, updates the authorized website live, sends test alerts, generates reports, and passes the agreed automated and human evaluation protocol.

## 10. Open product decisions

- Dataset sources, licensing, class balance, and annotation protocol.
- Selected four-point standard/buyer specification and exact size/grade/yield thresholds.
- Camera, lighting, line speed, fabric width, and evaluation hardware.
- CNN architecture and detector/classifier/autoencoder fusion policy.
- Media retention duration and whether MongoDB stores image bytes or object/file references.
- Alert severity, cooldown, escalation, and recipient policy.
