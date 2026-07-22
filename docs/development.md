# Development

Running OLcWave locally, the project layout, and the rules for contributing.

## Backend

Python 3.13, FastAPI, SQLAlchemy (async), managed with [uv](https://docs.astral.sh/uv/).

You need a Postgres to talk to. The easiest way is to start just the database with the dev compose file and run the API on your host:

```bash
# start only Postgres (and optionally the API) from the dev compose
docker compose -f docker-compose-dev.yaml up -d postgres
```

Then run the backend:

```bash
cd backend
uv sync                      # install dependencies from uv.lock
# make sure backend/.env has DB_HOST=localhost for host-side runs
uv run src/main.py           # starts uvicorn on 0.0.0.0:8000
```

`uv run src/main.py` runs the app defined in `src/main.py` (uvicorn on port 8000). Tables are created on startup. There are no migrations yet — the schema is created directly from the models.

If you prefer uvicorn with reload:

```bash
cd backend
uv run uvicorn --app-dir src main:app --reload --host 0.0.0.0 --port 8000
```

> `backend/.env` uses `DB_HOST=postgres` for Compose. For a host-side run against a local Postgres, set `DB_HOST=localhost`.

## Frontend

React 19 + Vite + TypeScript + Tailwind.

```bash
cd frontend
npm install
npm run dev        # Vite dev server on http://localhost:5173
```

Set `frontend/.env`:

```ini
VITE_API_URL=http://localhost:8000
VITE_SUB_URL_TEMPLATE=http://localhost:8000/sub/{uuid}
```

The backend's default `CORS_ORIGINS` already allow `http://localhost:5173`, so the dev server can call the API directly.

Other scripts:

```bash
npm run build      # type-check + production build → dist/
npm run lint       # oxlint
npm run preview    # serve the built dist/ locally
```

## Project structure

```
backend/
  src/
    main.py            # FastAPI app, router wiring, lifespan (tables + traffic loop)
    config.py          # env settings (pydantic-settings)
    database.py        # async engine, session factory, create_tables
    traffic.py         # background traffic collection + limit enforcement
    auth/              # admin login, JWT dependency
    users/             # local user records + traffic (router/service/db/models/schemas)
    profiles/          # YAML profile templates (router/service/db/models/schemas)
    olcrtc/            # Docker SDK wrapper + container service/schemas
    subscriptions/     # subscription generation, config→bundle/URI conversion
    rw/                # Remnawave SDK wrapper
  olcrtc/              # the OLCRTC container image (Dockerfile, entrypoint, Go proxy)
  Dockerfile           # API image
frontend/
  src/
    api/               # axios clients, one file per resource
    pages/             # one component per route (Dashboard, Users, Profiles, ...)
    components/        # ui/ (primitives), layout/, containers/, common/
    store/             # zustand auth store
    router/            # route table
    types/             # shared TypeScript types
    utils/             # formatting + hooks
caddy/Caddyfile        # reverse proxy config
docker-compose.yaml    # prod: caddy + api + postgres
docker-compose-dev.yaml# dev: api + postgres
```

Each backend module follows the same layering:

- `router.py` — HTTP endpoints (thin, auth-guarded).
- `service.py` — business logic, orchestration.
- `db.py` — database queries.
- `models.py` — SQLAlchemy tables.
- `schemas.py` — Pydantic request/response models.

### Where to add things

- **New API endpoint** → add a route in the relevant `router.py`, put logic in `service.py`, queries in `db.py`. Register new routers in `backend/src/main.py`.
- **New page** → add a component in `frontend/src/pages/`, register it in `frontend/src/router/index.tsx`, and add a nav entry in `frontend/src/components/layout/Sidebar.tsx`.
- **New API call from the frontend** → add a method to the matching client in `frontend/src/api/`, and a type in `frontend/src/types/index.ts`.
- **New reusable UI** → `frontend/src/components/ui/`.

---

## Development workflow and AI usage rules

This is an internal working agreement for OLcWave contributors. Read it before you touch the code.

### Backend — write it by hand

The backend must be developed **manually**. Do **not** use AI coding agents to generate backend implementation.

That covers everything under `backend/src/` written in:

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- business logic
- Docker integration
- external integrations (Remnawave, etc.)

**Why:** the backend holds the security-sensitive parts — authentication, user management, container control (which is effectively host root via the Docker socket), and traffic enforcement. This code must be written by a developer who fully understands what every line does. A subtle mistake here is a security or billing problem, not a cosmetic bug.

You **may** still use AI for:

- reading library documentation
- searching for solutions / approaches
- explaining an error message
- reviewing code you already wrote

You **may not** use AI to generate the backend implementation itself.

### Frontend — AI is allowed

AI coding agents are fine for the frontend.

**Why:** the frontend is mostly UI — components, pages, forms, tables, and data display. There's no secret and no privileged operation in the browser; the backend enforces everything.

AI is fine for:

- writing React components
- styling (Tailwind / CSS)
- refactoring UI
- generating repetitive code (tables, forms, list views)

**But every change must be reviewed by a developer before it's merged.** AI output that isn't understood doesn't get committed.

### Documentation — AI is allowed

You may use AI to help with docs.

AI is fine for:

- drafting README / guides
- describing architecture
- writing examples
- improving wording

**But the docs must be checked by hand and must match the real state of the code.** Documentation that describes features that don't exist is worse than no documentation.

### Summary

| Part of the project | AI agents | Rule |
|---------------------|-----------|------|
| Backend | No | Write by hand |
| Frontend | Yes | Review every change |
| Documentation | Yes | Verify it matches the code |
