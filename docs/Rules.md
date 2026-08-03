# FabriX-QA — Coding Conventions & Agent Rules

> **Version:** 1.0 — Initial Scaffold  
> **Last Updated:** 2026-08-04  
> **This file is binding for all human developers and AI coding agents working on this codebase.**

---

## 1. General Principles

1. **Readability over cleverness.** Code is read 10× more than it is written. Prefer explicit over implicit.
2. **Every module must have a purpose comment at the top.** No exceptions.
3. **Never implement features not requested in the current task.** Scope creep introduces bugs.
4. **Leave `TODO:` comments** for planned but not-yet-implemented logic. Never leave dead code silently.
5. **All secrets come from `.env`.** Never hardcode credentials, tokens, or secrets.

---

## 2. Folder & File Naming Rules

| Context | Convention | Example |
|---|---|---|
| Python files | `snake_case.py` | `grading_engine.py` |
| Python classes | `PascalCase` | `GradingEngine` |
| Python functions/vars | `snake_case` | `compute_grade()` |
| TypeScript files | `camelCase.ts` or `PascalCase.tsx` for components | `apiClient.ts`, `GradeCard.tsx` |
| Next.js pages | `page.tsx` inside route folder | `app/reports/page.tsx` |
| Next.js components | `PascalCase.tsx` | `DefectFeedCard.tsx` |
| CSS/Tailwind classes | Follow Tailwind naming; use `cn()` utility | `cn('flex', isActive && 'bg-brand-accent')` |
| Environment variables | `SCREAMING_SNAKE_CASE` | `JWT_SECRET_KEY` |
| Docker services | `lowercase_snake` | `fabrix_backend` |
| Database tables | `snake_case` (plural) | `defect_records`, `grade_records` |
| MongoDB collections | `snake_case` (plural) | `defect_images` |
| Git branches | `type/short-description` | `feat/grading-engine` |

---

## 3. Python (Backend & AI)

### 3.1 Style
- Formatter: **Black** (line length: 100)
- Linter: **Ruff** (replaces flake8 + isort + pyupgrade)
- Type hints: **mandatory** on all function signatures
- Docstrings: **Google style** for all public classes and functions

### 3.2 FastAPI Conventions
- All route handlers must be `async def`
- Use Pydantic v2 `BaseModel` for all request/response schemas
- Use `Annotated[..., Depends(...)]` dependency injection pattern
- Return types must be explicitly declared on all route handlers
- HTTP exceptions use `raise HTTPException(status_code=..., detail=...)`

### 3.3 Database
- All SQLAlchemy queries must be `async` (use `AsyncSession`)
- Never use `session.query()` (legacy) — use `select()` statements
- All database migrations via **Alembic** — never `Base.metadata.create_all()` in production
- MongoDB operations via **Motor** async client only

### 3.4 AI/CV Module
- All model weights referenced by path from environment variable — never hardcoded
- Inference functions must accept `np.ndarray` (BGR, HWC) and return typed dataclasses
- Training scripts must log to MLflow: params, metrics, and model artifacts
- Albumentations transforms defined in `preprocessing/augmentation.py` — never inline

---

## 4. TypeScript / Next.js (Frontend)

### 4.1 Style
- Formatter: **Prettier** (default config)
- Linter: **ESLint** with `next/core-web-vitals`
- Strict TypeScript: `"strict": true` in `tsconfig.json`
- No `any` types — use `unknown` + type guards if necessary

### 4.2 Component Conventions
- All React components: **functional components with explicit prop types**
- Use `interface` for prop types (prefer over `type` for objects)
- Co-locate component-specific types in the same file
- Use `cn()` from `lib/utils.ts` for all conditional class merging

### 4.3 State Management
- Global state: **Zustand** stores in `lib/store/`
- Server state / fetching: use **SWR** or direct `apiClient` with `useEffect`
- Form state: **React Hook Form** + **Zod** validation schemas

### 4.4 API Calls
- All API calls go through `lib/api.ts` (axios instance with JWT interceptor)
- Never call `fetch()` directly — always use the configured `apiClient`
- WebSocket connections managed in `lib/websocket.ts`

---

## 5. Git Commit Conventions

Follow **Conventional Commits** spec: `type(scope): description`

| Type | When to Use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `chore` | Build, tooling, deps — no prod code change |
| `refactor` | Code restructure (no behavior change) |
| `test` | Adding or fixing tests |
| `perf` | Performance improvement |
| `ci` | CI/CD pipeline changes |

**Examples:**
```
feat(grading): implement grade A/B/C/D computation logic
fix(auth): resolve JWT expiry not being checked on refresh
docs(memory): update Memory.md after grading engine completion
chore(deps): bump ultralytics to 8.2.56
```

---

## 6. Testing Rules

- All backend services must have unit tests in `backend/tests/`
- Use `pytest` + `pytest-asyncio` for async tests
- Minimum coverage target: **70%** for service layer
- Frontend: component tests with **React Testing Library** (future)
- AI module: training scripts must log validation mAP per epoch
- Never merge code that breaks existing tests

---

## 7. AI Agent Rules (CRITICAL — READ FIRST)

> These rules apply to any AI coding assistant (Claude, Gemini, Copilot, etc.) working on this codebase.

### 7.1 Before Starting Any Task
1. **Read `docs/Memory.md` first.** It is the authoritative record of what has been built and what decisions were made. Do not assume — read it.
2. **Read the relevant module documentation** in `docs/Architecture.md` before touching any module.
3. **Check `docs/Phases.md`** to understand what phase is currently active and what is in scope.

### 7.2 Scope Control
- **Only implement what is explicitly requested.** Do not add unrequested features, refactors, or "improvements."
- If you notice a bug or issue outside your task scope, document it in `Memory.md` as a known issue — do not fix it unsolicited.
- **Ask before making architectural decisions.** If the task requires a design decision not covered in `Architecture.md`, stop and ask.

### 7.3 After Completing Any Task
1. **Update `docs/Memory.md`** with:
   - What was built
   - What decisions were made and why
   - What TODOs remain
   - Any known issues discovered
2. **Update the relevant doc file** if the implementation changes or extends the architecture.
3. **Update `docs/Phases.md`** — check off completed items.
4. **Run linting and tests** before declaring a task complete.

### 7.4 Code Style Compliance
- Follow all conventions in Sections 2–6 of this document
- Never introduce new dependencies without documenting them in `Memory.md`
- Always add type hints, docstrings, and module-level purpose comments

### 7.5 Prohibited Actions
- ❌ Never delete or overwrite files without explicit instruction
- ❌ Never commit or push to `main` directly
- ❌ Never hardcode secrets, credentials, or IPs
- ❌ Never bypass existing tests or skip linting
- ❌ Never modify `docs/Memory.md` destructively — always append
