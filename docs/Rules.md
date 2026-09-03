# FabriX-QA Engineering and Collaboration Rules

**Version:** 1.2
**Binding for:** both student developers and every AI coding agent
**Last updated:** 2026-09-03

## 1. Mandatory session protocol

### Before every task

1. Read `docs/Memory.md` first. It is the single source of truth for what is built, decided, open, and known to be broken.
2. Read the relevant sections of `docs/PRD.md`, `docs/Architecture.md`, `docs/Rules.md`, `docs/Phases.md`, and `docs/Design.md`.
3. Inspect the current branch and working tree. Preserve unrelated human or agent changes.
4. Confirm the requested work belongs to the active phase and does not contradict a recorded decision.
5. Do not describe a placeholder, target design, or unchecked phase item as implemented.

### After every task

1. Update `docs/Memory.md` with the date, what actually changed, decisions and rationale, verification performed, known issues, and next work.
2. Update every affected living document among PRD, Architecture, Rules, Phases, and Design.
3. Mark phase checkboxes complete only when implementation and appropriate verification are complete.
4. Run checks proportional to the change and record any checks that could not run.
5. Review the diff for secrets, generated artifacts, accidental scope changes, and inaccurate documentation.

This protocol is never optional, including for small fixes and documentation-only work.

## 2. Git workflow and protected branches

The established flow is:

```text
features/zarwan ─┐
                 ├─> dev ─> main
features/kaynat ─┘
```

- All scaffolding and implementation work occurs on the currently checked-out feature branch.
- `main` and `dev` are protected.
- Never commit or push directly to `main` or `dev`.
- Never force-push protected branches. Do not rewrite shared history.
- Merge feature branches into `dev` through a pull request.
- Merge `dev` into `main` through a pull request.
- Every protected-branch PR requires at least one approval and passing CI.
- CI is expected at `.github/workflows/ci.yml`: Ruff, Black, and pytest for the backend; lint and build for the frontend.
- Do not weaken branch protection, bypass CI, dismiss reviews, or change this workflow without explicit team agreement.
- Rebase/merge conflict resolution must preserve the other teammate's work.
- Use small, reviewable commits following Conventional Commits, for example `feat(grading): add four-point calculation` or `docs(memory): record scoring decision`.
- Never commit secrets, local datasets, model weights, generated heatmaps, database volumes, or `.env`.

If the documented CI file or protection state is not visible locally, record the discrepancy; do not invent or alter protection settings.

## 3. Scope and decision discipline

- Implement only the requested phase/task. A clean scaffold is not permission to implement features.
- Prefer the smallest design that satisfies a two-person FYP team and a website-only product.
- FastAPI is the single backend. Do not introduce a Node.js API, microservice split, queue, cache, or new database without evidence, team approval, and updated architecture.
- New dependencies require a concrete need, compatibility verification, exact pinning, and a Memory/Architecture entry.
- Before adding or changing a Python dependency, run `python -m pip show <package>` in the target environment or inspect the package's canonical PyPI page to confirm its distribution name, import name, and purpose. Also check the consuming framework's exact-version documentation, optional requirements, and relevant source/runtime imports. Installation success alone is insufficient; different distribution/import names or an empty `Required-by` field do not prove a package is wrong or unused.
- For this project's currently resolved Starlette 1.6.0, `httpx2==2.12.0` is the verified TestClient dependency; the earlier claim that HTTPX2 was unrelated was incorrect. Reassess against upstream evidence when upgrading Starlette. FastAPI-Mail 1.6.8 separately requires `httpx>=0.28.1`, so both distributions are expected in the backend environment. See Memory's 2026-09-03 verification record and source link.
- Product thresholds must come from data, a named specification, buyer policy, or domain-expert validation. Never invent four-point grade or yield-loss thresholds and present them as facts.
- Architectural uncertainty is recorded as an open decision, not silently resolved.
- Human corrections and policy changes must be auditable; never erase original AI/scoring results.

## 4. Python standards

- Runtime baseline: Python 3.12.
- Format with Black; lint with Ruff; test with pytest and pytest-asyncio.
- Use type hints on public functions, methods, and boundary data.
- Use Pydantic v2 models at API/event boundaries.
- Keep FastAPI route handlers thin; business logic belongs in services.
- Use async I/O for database, WebSocket, and provider operations; do not label CPU-heavy inference async and then block the event loop.
- Use SQLAlchemy 2.x patterns and Alembic for every PostgreSQL schema change.
- Use PyMongo's native async API for new MongoDB code; do not introduce Motor.
- Catch specific exceptions, log actionable context without secrets, and preserve causal exceptions.
- Add deterministic unit tests for grading, conversions, thresholds, and RBAC boundaries.
- AI experiments must record seed, dataset/split version, transforms, weights/config, package versions, hardware, metrics, and artifact hashes.

## 5. TypeScript and website standards

- Runtime baseline: Node.js 22; strict TypeScript is mandatory.
- Use the Next.js App Router, React functional components, Tailwind CSS, and Recharts.
- Do not add a second backend or Socket.IO; use browser-native WebSockets with FastAPI.
- Treat backend authorization as authoritative. Hidden controls are not access control.
- Avoid `any`; validate unknown network data before use.
- Keep server-only secrets and provider credentials out of `NEXT_PUBLIC_*` variables.
- Every live view must define loading, disconnected, stale, empty, error, and reconnecting states.
- Charts require accessible titles/labels, units, legends, tooltips, and a non-chart summary or table where needed.
- The product is desktop/factory-monitor focused, not a mobile application; reasonable browser resizing must still fail gracefully.

## 6. AI, data, and grading standards

- Raw datasets and model weights stay out of Git. Commit manifests, licenses/attribution, checksums, class maps, and preparation instructions.
- Split data by source/roll where possible to prevent near-duplicate frame leakage.
- Never evaluate on the training set or tune against the final test set.
- Report per-class precision, recall, F1, confusion matrix, mAP, latency, and hardware; report anomaly metrics separately.
- Preserve coordinate transforms from source frame to ROI/model/image/heatmap spaces.
- Version and test four-point rules independently of model confidence.
- Four-point points, A/B/C/D mapping, and yield-loss estimation are distinct concepts. Do not conflate them.
- Retain model and rule provenance for every computed roll result.
- Use synthetic or licensed data only; document dataset rights and retention.

## 7. Databases and cross-store consistency

- PostgreSQL owns structured identities and audited business state.
- MongoDB owns defect-media documents/metadata linked by stable IDs.
- Do not rely on cross-database transactions. Use idempotency, explicit status, retry, and reconciliation.
- Database schemas change only through reviewed migrations/init revisions.
- Store timestamps in UTC and render the user's timezone at presentation boundaries.
- Define indexes from measured query patterns, not guesses.
- Never store plaintext passwords, JWTs, Twilio tokens, SMTP passwords, or unnecessary personal data.

## 8. Security and notifications

- Deny access by default and test the entire role-permission matrix.
- Hash passwords using an approved adaptive algorithm; the current dependency choice is Argon2 via `pwdlib`.
- Validate JWT issuer/audience/expiry and WebSocket authorization when implemented.
- Apply rate/size limits at trust boundaries.
- Notification delivery must be non-blocking, deduplicated, retry-aware, and auditable.
- Use provider test credentials/fakes in automated tests; never send real alerts from CI.
- Production-like deployment requires TLS, secret management, backups, and restore testing.

## 9. Documentation and code quality

- Every source module begins with a concise purpose comment/docstring.
- Comments explain intent, constraints, or non-obvious reasoning—not line-by-line mechanics.
- Public behavior requires tests and updated docs.
- Use UTF-8, consistent names, and small cohesive modules.
- Do not leave dead code, fabricated metrics, or TODOs without an owner/phase.
- A task is complete only when code, tests, and living docs agree with the real repository state.

## 10. Prohibited actions

- Direct or force pushes to `main`/`dev`.
- Branch-protection or CI bypass.
- Committing credentials, datasets, model weights, runtime media, or generated database data.
- Silent dependency or architecture expansion.
- Claims that unmeasured accuracy/performance has been achieved.
- Destructive editing of another teammate's unrelated work.
- Skipping the Memory-first and Memory-last protocol.
