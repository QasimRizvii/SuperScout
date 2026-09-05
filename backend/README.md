# SuperScout Backend

FastAPI backend for the SuperScout Cricket Intelligence Platform.

---

## Requirements

- Python 3.11+
- PostgreSQL 15+ (optional for Phase 1 — the API starts without it)

---

## Setup

### 1. Create a virtual environment

```bash
cd backend
python -m venv .venv
```

**Activate it:**

- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- Windows (CMD): `.venv\Scripts\activate.bat`
- macOS / Linux: `source .venv/bin/activate`

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the root `.env.example` to `.env` in the project root and fill in your values:

```bash
# From the superscout/ root
cp .env.example .env
```

Key variables:

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://superscout:password@localhost:5432/superscout_db` |
| `API_HOST` | Host to bind the server to | `0.0.0.0` |
| `API_PORT` | Port to listen on | `8000` |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins | `http://localhost:3000` |

---

## Running the Backend

From the `backend/` directory with the virtual environment active:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- **API**: `http://localhost:8000`
- **Docs (Swagger UI)**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/api/v1/health`

---

## Available Endpoints (Phase 1)

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/health` | API and database health status |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc documentation |

---

## Running Tests

```bash
pytest tests/ -v
```

Expected output (Phase 1):

```
tests/test_health.py::test_app_starts                    PASSED
tests/test_health.py::test_health_endpoint_returns_200   PASSED
tests/test_health.py::test_health_response_schema        PASSED
tests/test_health.py::test_health_database_field_present PASSED
tests/test_health.py::test_health_response_content_type  PASSED
tests/test_health.py::test_unknown_route_returns_404     PASSED
```

---

## PostgreSQL Setup

### Option A — Docker (recommended)

```bash
# From the superscout/ root
docker-compose up db -d
```

### Option B — Local PostgreSQL

1. Install PostgreSQL 15+
2. Create the database and user:

```sql
CREATE USER superscout WITH PASSWORD 'your_secure_password';
CREATE DATABASE superscout_db OWNER superscout;
GRANT ALL PRIVILEGES ON DATABASE superscout_db TO superscout;
```

3. Set `DATABASE_URL` in your `.env`:

```
DATABASE_URL=postgresql://superscout:your_secure_password@localhost:5432/superscout_db
```

> The health endpoint will show `"database": {"status": "unavailable"}` if PostgreSQL is not running.
> The backend itself will still start and function.

---

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI application factory
│   ├── api/
│   │   └── v1/
│   │       ├── router.py    # v1 route aggregator
│   │       └── endpoints/
│   │           └── health.py
│   ├── core/
│   │   ├── config.py        # Pydantic settings (env vars)
│   │   └── logging.py       # Logging configuration
│   ├── db/
│   │   ├── base.py          # SQLAlchemy declarative base
│   │   ├── session.py       # Engine + session factory
│   │   └── health.py        # Database health check
│   ├── models/              # ORM models (Phase 2+)
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic (Phase 2+)
│   └── utils/               # Shared utilities (Phase 2+)
└── tests/
    ├── conftest.py
    └── test_health.py
```
