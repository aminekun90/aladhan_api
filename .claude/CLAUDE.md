# aladhan_api — Claude Context

## Project Overview
Full-stack Islamic prayer times application. Backend: FastAPI (Python) implementing prayer time calculations from scratch. Frontend: React 19 with Material UI and TanStack Query. Features Sonos speaker integration for azan playback, PostgreSQL persistence, APScheduler for automated tasks.

## Project Structure
```
aladhan_api/
├── backend/          # FastAPI Python app
├── frontend/         # React 19 + TypeScript app
├── data_tools/       # Python data utilities
├── docker_compose.yml
└── DOCKERFILE
```

## Backend — FastAPI (Python)
**Python:** `>=3.12` | **Package manager:** `uv`

### Key Dependencies
- `fastapi`, `uvicorn[standard]` — API server
- `sqlalchemy`, `alembic` — ORM + migrations
- `psycopg2-binary` — PostgreSQL driver
- `apscheduler` — periodic tasks (prayer time scheduling)
- `soco` — Sonos speaker control
- `python-dotenv` — environment config

### Backend Commands
```bash
# Dev server (from backend/)
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest

# Database migrations
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "description"

# Docker
docker compose up -d          # Start all services
docker compose down           # Stop
docker compose logs -f        # Tail logs
```

### Backend Conventions
- **Type hints everywhere** — all function signatures must have type annotations
- **Pydantic models** for request/response validation — never raw dicts as API contracts
- **SQLAlchemy models** in `models/`, Pydantic schemas in `schemas/`
- **Alembic migrations** for every schema change — never modify DB directly
- **`.env` file** for secrets — never hardcode credentials
- **Timezone:** always `Europe/Paris` for prayer time calculations

## Frontend — React 19 + TypeScript
**Package manager:** `yarn`

### Key Dependencies
- `react 19`, `typescript` — base
- `@mui/material` — UI components
- `@tanstack/react-query` — server state / data fetching
- `axios` — HTTP client
- `dayjs` — date manipulation
- `i18next` — internationalization
- `vite` — build tool

### Frontend Commands
```bash
# From frontend/
yarn start            # Dev server (Vite)
yarn build            # Production build
yarn lint             # ESLint check
yarn preview          # Preview production build
```

### Frontend Conventions
- **TanStack Query** for all API calls — no bare `useEffect` for data fetching
- **i18next** for all user-visible strings — no hardcoded French/English
- **MUI components** consistently — no mixing with other UI libs
- **dayjs** for all date/time — never `new Date()` for formatting
- **TypeScript strict** — no `any`
- **Axios instance** with base URL config — never raw `fetch()`

## Docker / Infrastructure
```bash
docker compose up -d          # Full stack (API + DB)
docker compose up adhan-api   # API only
```

Environment variables (see `docker_compose.yml`):
- `TZ=Europe/Paris` — critical for prayer time accuracy
- `UVICORN_HOST=0.0.0.0`
- `UVICORN_PORT=8000`

## DB: PostgreSQL
- Managed via SQLAlchemy + Alembic
- Always run `alembic upgrade head` after pulling new migrations
- Never run raw SQL migrations manually
