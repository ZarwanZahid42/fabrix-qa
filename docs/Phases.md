# FabriX-QA Development Phases

**Last updated:** 2026-08-30
**Current state:** Foundation scaffold complete; Phase 1 requirements/design work is next
**Legend:** `[ ]` not complete, `[x]` complete

A checkbox is complete only when its artifact exists, relevant verification passes, and Memory plus affected docs reflect reality.

## Foundation scaffold (completed)

- [x] Create frontend, backend, AI, edge, Docker, and docs boundaries.
- [x] Add minimal buildable Next.js and FastAPI entry points without product features.
- [x] Add purpose-only placeholders for planned implementation modules.
- [x] Pin current Python 3.12 backend and AI/CV dependencies.
- [x] Add local PostgreSQL/MongoDB Docker Compose scaffold.
- [x] Add comprehensive `.gitignore` and `.env.example`.
- [x] Establish PRD, architecture, rules, phases, design, and memory baselines.
- [x] Add and validate `.github/workflows/ci.yml` with passing Python 3.12 backend and Node.js 22 frontend checks on the feature branch.

## External repository administration (manual follow-up)

- [ ] After the workflow is merged, configure GitHub rulesets for `main` and `dev` to require the exact `backend` and `frontend` checks. This must be done manually in GitHub settings and was not part of feature-branch scaffolding.

## Phase 1 — Requirements & Design

**Goal:** remove product ambiguity before feature code and establish measurable acceptance criteria.

- [ ] Interview/validate workflows with an operator, maintenance stakeholder, and manager proxy.
- [ ] Select and cite the applicable four-point inspection standard or buyer specification.
- [ ] Validate defect-size point rules, units, repeated/edge defect treatment, and maximum points.
- [ ] Define configurable A/B/C/D thresholds separately from four-point scoring.
- [ ] Define and validate the yield-loss formula and required production inputs.
- [ ] Produce the complete Operator/Maintenance/Manager permission matrix.
- [ ] Define roll, line, camera, inspection, event, alert, and audit lifecycle/state diagrams.
- [ ] Finalize API and versioned WebSocket event contracts.
- [ ] Finalize PostgreSQL entities and MongoDB media-document ownership/retention.
- [ ] Decide JWT access/refresh/revocation approach and threat model.
- [ ] Audit datasets for licensing, fabric relevance, class coverage, imbalance, and leakage risks.
- [ ] Define annotation guidelines for hole, stain, weave error, and pattern break.
- [ ] Establish train/validation/test split policy by roll/source.
- [ ] Name evaluation hardware and set evidence-based accuracy/latency/FPS targets.
- [ ] Create dashboard wireframes and conduct a short usability review.
- [ ] Define automated test strategy, fixtures, coverage targets, and traceability matrix.
- [ ] Review and approve PRD, Architecture, and Design baselines as a two-person team.

**Exit gate:** requirements, scoring policy, contracts, data plan, wireframes, and measurable acceptance criteria are reviewed and no critical ambiguity blocks implementation.

## Phase 2 — AI & Vision Development

**Goal:** build and evaluate a reproducible offline computer-vision pipeline.

- [ ] Create licensed dataset manifests, checksums, attribution, and preparation instructions.
- [ ] Implement annotation conversion and validation.
- [ ] Implement ROI-aware preprocessing and Albumentations transforms.
- [ ] Add deterministic split and leakage checks.
- [ ] Train and tune a YOLOv8 baseline.
- [ ] Select and train the CNN classifier architecture.
- [ ] Train and calibrate the convolutional autoencoder anomaly model.
- [ ] Select and validate the heatmap/localization method.
- [ ] Define and calibrate detector/classifier/autoencoder fusion.
- [ ] Implement typed inference result contracts and model provenance.
- [ ] Evaluate per-class precision, recall, F1, mAP@0.5, mAP@0.5:0.95, confusion matrix, and calibration.
- [ ] Evaluate anomaly detection separately with appropriate ROC/PR metrics.
- [ ] Benchmark preprocessing/inference latency and throughput on named hardware.
- [ ] Perform qualitative error analysis across fabrics, lighting, and defect sizes.
- [ ] Freeze a reproducible candidate model bundle and document limitations.

**Exit gate:** a versioned offline pipeline meets the approved evidence threshold without test-set leakage and can reproduce evaluation results from documented inputs.

## Phase 3 — Edge & Logic Integration

**Goal:** process bounded live/recorded streams, persist evidence, and calculate auditable roll outcomes.

- [ ] Implement source lifecycle, reconnect, timestamps, frame IDs, and bounded backpressure.
- [ ] Implement ROI selection, validation, coordinate transforms, and persistence.
- [ ] Integrate edge frames with the frozen inference contract.
- [ ] Add PostgreSQL migrations and async persistence.
- [ ] Add MongoDB media-document persistence and retention status.
- [ ] Implement stable IDs, idempotent writes, partial-failure status, and reconciliation.
- [ ] Implement versioned four-point score contributions and golden calculation tests.
- [ ] Implement configurable A/B/C/D grade mapping and boundary tests.
- [ ] Implement documented yield-loss calculation and validation.
- [ ] Implement roll start/progress/completion lifecycle.
- [ ] Implement JWT authentication and deny-by-default RBAC.
- [ ] Implement versioned native WebSocket event envelopes and authenticated connections.
- [ ] Implement alert policy evaluation, cooldown/deduplication, Twilio, and email adapters.
- [ ] Add audit events for auth, policy, grade correction, user, and export actions.
- [ ] Run camera/video → AI → both databases → grade → WebSocket integration tests.
- [ ] Test camera, database, client, and notification failure recovery.

**Exit gate:** a representative stream produces traceable, deduplicated defect events and an auditable roll grade while recovering safely from tested failures.

## Phase 4 — Fullstack & Dashboard

**Goal:** deliver the role-gated website workflow from live monitoring through reports.

- [ ] Build accessible login/logout/session-expiry flows.
- [ ] Build role-aware navigation backed by server authorization.
- [ ] Build the operations overview and line/roll status.
- [ ] Build live defect feed with heatmap/media inspection.
- [ ] Handle connected, reconnecting, stale, disconnected, empty, loading, and error states.
- [ ] Build four-point score, A/B/C/D grade, and yield-loss summaries with units/provenance.
- [ ] Build Recharts grade, defect-rate/type, and yield-loss trends.
- [ ] Build alert history, acknowledgement, and delivery-status workflows.
- [ ] Build manager roll history, filters, report detail, and export.
- [ ] Build authorized user/role and quality-policy administration.
- [ ] Provide accessible table/text alternatives for important chart information.
- [ ] Add frontend validation, typed API/event parsing, and safe error handling.
- [ ] Add component, integration, and role-based end-to-end tests.
- [ ] Conduct operator/maintenance/manager usability walkthroughs and record changes.

**Exit gate:** each role can complete approved website workflows with correct authorization, understandable live state, and accessible evidence.

## Phase 5 — Testing & Optimization

**Goal:** prove quality, harden deployment, and prepare an honest faculty demonstration.

- [ ] Complete the requirements-to-test traceability matrix.
- [ ] Pass backend Ruff, Black, pytest, migration, and security checks.
- [ ] Pass frontend lint, production build, accessibility, and end-to-end checks.
- [ ] Run full held-out AI evaluation and document confidence intervals/limitations.
- [ ] Benchmark sustained end-to-end FPS, latency percentiles, CPU/GPU/RAM, and queue depth.
- [ ] Optimize only measured bottlenecks and record before/after evidence.
- [ ] Run RBAC, JWT, input-validation, secrets, dependency, and WebSocket security review.
- [ ] Test notification retry/deduplication without sending from CI.
- [ ] Test backup/restore and cross-store reconciliation.
- [ ] Build production-ready immutable images, health checks, limits, TLS, and secret handling.
- [ ] Test failure/recovery for camera, AI, PostgreSQL, MongoDB, providers, and browser reconnect.
- [ ] Conduct final usability and faculty-demo rehearsals.
- [ ] Produce final technical report, architecture diagrams, experiment appendix, user guide, and demo video.
- [ ] Record known limitations, ethical considerations, and future work.
- [ ] Merge through protected PRs only after one approval and passing CI.

**Exit gate:** the reproducible release passes the agreed acceptance suite, deployment/recovery checks, and an evidence-based demonstration with no fabricated claims.
