# Sahaayak backend

A FastAPI backend for the Sahaayak demo. It replaces the frontend's six
`localStorage` keys with real server-backed resources and moves the
eligibility engine and the deterministic explanation layer server-side, so
matching logic exists in exactly one place instead of being duplicated in
the browser. Every scheme and document is still fictional demo data - this
backend does not connect to, scrape, or represent any real government
system.

## Quick start

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # or `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp .env.example .env          # adjust if needed; SQLite works out of the box
alembic upgrade head
uvicorn app.main:app --reload
```

The API comes up at `http://127.0.0.1:8000`, with interactive docs at
`/docs`. On startup it also seeds the six demo schemes if the `schemes`
table is empty (`app/seed/schemes_seed.py`), so a fresh SQLite database is
immediately usable.

Run the tests:

```bash
pytest
```

## Anonymous session model

There are no user accounts anywhere in this API - no username, password,
OTP, or identity verification. `POST /api/session` creates a row in
`anonymous_sessions` holding nothing but a UUID and a timestamp, and
returns it to the browser as a **signed, httpOnly cookie**
(`sahaayak_session`) containing that UUID, signed with `itsdangerous`
using `SESSION_SECRET`. Every other endpoint resolves the session from
that cookie via `app/deps.py::get_current_session` and 401s if it's
missing, invalid, or unknown.

We chose a signed cookie over a bearer token because the frontend is a
browser SPA talking to this API same-site during local dev, and an
httpOnly cookie can't be read or exfiltrated by injected client-side
JavaScript the way a token sitting in `localStorage` could. The cookie
carries no personal data - just an opaque identifier - so even if it were
intercepted, nothing about the underlying person is exposed beyond "this
browser has visited before."

This mirrors the frontend's original privacy stance (see the root
`README.md` and `src/types.ts`): the whole point of Sahaayak is that a
person can get useful guidance without proving who they are. The
`ProfileIn` schema (`app/schemas/profile.py`) enforces the same boundary
at the API layer with `extra="forbid"` - any field that isn't part of the
known, deliberately-non-identifying `Profile` shape (no name, phone,
Aadhaar, bank account, or precise address) is rejected with `422` rather
than silently accepted.

## Architecture

```text
backend/
  app/
    main.py                     FastAPI app, CORS, router wiring, startup seed
    config.py                   Settings (DATABASE_URL, SESSION_SECRET, CORS_ORIGINS)
    db.py                       SQLModel engine/session
    deps.py                     Cookie-session auth dependency
    models/                     SQLModel tables (snake_case columns)
    schemas/                    Pydantic request/response shapes (camelCase,
                                 matching src/types.ts field-for-field)
    services/
      eligibility.py            Direct port of src/lib/eligibility.ts
      explanations.py           Direct port of src/lib/explanations.ts
      explanation_provider.py   ExplanationProvider seam (see below)
      reference_generator.py    Deterministic SHY-{year}-{5 chars} codes
      mapper.py                 snake_case ORM rows <-> camelCase dicts
      scheme_repo.py            Scheme+Rule loading helpers
      profile_repo.py           Profile lookup helper
    routers/                    One module per resource
    seed/
      document_labels.py        Transcribed from src/data/schemes.ts
      schemes_seed.py           The 6 demo schemes, transcribed verbatim
  alembic/                      Migrations (initial schema in versions/)
  tests/                        pytest + httpx.AsyncClient
```

### Why the engine is dict-based, not ORM-based

`services/eligibility.py` and `services/explanations.py` operate on plain
`dict`s keyed exactly like the frontend's TypeScript interfaces
(`age`, `incomeBand`, `requiredDocuments`, ...), not on SQLModel rows. This
was a deliberate choice: it means those two files are a checkable,
near-line-for-line mirror of `src/lib/eligibility.ts` and
`src/lib/explanations.ts`, with no ORM/session concerns mixed in. The
translation between snake_case DB columns and camelCase engine/API dicts
happens in one place, `services/mapper.py`.

### Field naming

Pydantic schemas intentionally use the *same* camelCase field names as the
frontend TypeScript types (`householdSize`, `incomeBand`, `missingInfo`,
...) rather than Python's usual snake_case convention. This is deliberate:
it keeps `fetch("/api/profile")` a close-to-mechanical swap for the
current `localStorage.getItem("sahaayak-profile")` reads, and it makes any
type drift between frontend and backend immediately visible as a naming
mismatch rather than something hidden behind an alias config. The SQLModel
tables underneath still use conventional snake_case columns.

### The `ExplanationProvider` seam

`services/explanation_provider.py` defines a small `Protocol` with the
same four operations as the frontend's `explanations.ts`
(`simple_terms`, `fit_explanation`, `plan_tasks`, `explain_task`). Routers
depend on `get_explanation_provider()`, not on `services/explanations.py`
directly. Today it always returns `DeterministicExplanationProvider`, a
thin wrapper with zero network calls - no LLM/API-key integration is
built or stubbed here. The seam exists so a future real-LLM provider
could implement the same interface and be swapped in via
`get_explanation_provider()` without touching router code, but building
that provider is explicitly out of scope for this prototype.

### Multi-plan support

The frontend currently keeps one active plan/reference at a time
(`localStorage`). The backend's data model doesn't have that limitation:
`Plan` rows are keyed by `(session_id, scheme_id)`, so a session can hold
one plan per scheme it has started, and `GET /api/plans` returns all of
them. `POST /api/plans/{scheme_id}` is idempotent per scheme - calling it
again regenerates that scheme's task list from the current profile while
preserving any checkbox state the user already set (mirroring
`planTasks(existing)` in the original TypeScript), rather than creating a
duplicate plan.

### Deterministic reference codes

The frontend generates `SHY-2026-#####` with `Math.random()`
(`src/components/Handoff.tsx`), which is neither reproducible nor
collision-checked. `services/reference_generator.py::generate_reference_code`
instead hashes `(session_id, scheme_id, timestamp, attempt)` with SHA-256
and Base32-encodes a slice of the digest (Base32 avoids visually
ambiguous characters like `0`/`O` and `1`/`I`, since this code is meant to
be read and typed by a person). `routers/handoff.py` still checks the
result against the `reference_requests.reference_code` unique constraint
and retries with an incremented `attempt` on the (extremely unlikely)
event of a collision, rather than assuming the hash is automatically
unique.

## API summary

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/session` | Create an anonymous session + blank profile, set the session cookie |
| GET | `/api/schemes` | List all seeded demo schemes + document labels |
| GET | `/api/schemes/{id}` | Single scheme detail |
| GET | `/api/schemes/{id}/explanation` | `fitExplanation()` for that scheme against the current profile |
| GET | `/api/profile` | Current session's profile |
| PUT | `/api/profile` | Replace the current session's profile |
| POST | `/api/profile/demo` | Load the seeded demo profile (mirrors "Use demo profile") |
| POST | `/api/match` | Run the eligibility engine; returns `matches[]` + `simpleTerms` |
| GET | `/api/plans` | All plans for this session |
| POST | `/api/plans/{schemeId}` | Create/regenerate a plan's checklist for a scheme |
| PATCH | `/api/plans/{planId}/tasks/{taskId}` | Toggle a task's done state |
| POST | `/api/plans/{planId}/explain` | Answer one of the 3 canned questions about a task |
| POST | `/api/handoff` | Create a synthetic readiness reference for a plan |
| GET | `/api/references/{code}` | Look up a previously created reference (session-scoped) |

Every response mirrors the corresponding frontend component's expected
shape (see `src/components/*.tsx` and `src/types.ts`), so wiring up
`fetch` calls in place of `localStorage` reads should be close to
mechanical.

## Environment variables

See `.env.example`:

- `DATABASE_URL` - SQLite by default; point at Postgres (`postgresql://...`)
  for a real deployment.
- `SESSION_SECRET` - signs the session cookie. Change it for any real
  deployment; the checked-in default is intentionally weak.
- `CORS_ORIGINS` - comma-separated allow-list; defaults to the Vite dev
  server's origin (`http://localhost:5173`).

## Limitations

- All scheme data and eligibility rules are fictional demo content,
  transcribed from `src/data/schemes.ts` - not real policy.
- No real-LLM explanation provider is implemented; see "The
  `ExplanationProvider` seam" above.
- The anonymous session model has no expiry/rotation policy beyond the
  cookie's 30-day `max-age`, and no way for a person to delete their data
  short of a database operation - a real deployment would need an
  explicit data-deletion endpoint.
- CORS is permissive on methods/headers (`*`) for hackathon convenience;
  a production deployment should narrow this.
