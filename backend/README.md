# Postit API (FastAPI)

Async, production-grade backend for Postit: auth, workspaces & RBAC, social connections,
posts + the per-platform rewrite engine, analytics, Paddle billing with admin-managed plans,
notifications, brand voice, and a superuser admin API.

## Stack
FastAPI · SQLAlchemy 2.0 (async) · Alembic · Pydantic v2 · PyJWT (access + rotating refresh) ·
argon2 · Redis (optional, in-memory fallback) · Paddle (httpx) · MySQL 8 (prod) / SQLite (dev).

## Quick start (local, SQLite — no Docker needed)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                     # defaults already work for SQLite

alembic upgrade head                     # create schema
python -m app.db.seed                    # demo data
uvicorn app.main:app --reload --port 8000
```

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/healthz

### Seeded logins
| Role        | Email              | Password      |
| ----------- | ------------------ | ------------- |
| Super admin | `admin@postit.app` | `admin12345`  |
| Demo owner  | `rina@maple.co`    | `password123` |

## Production (MySQL + Redis via Docker)

```bash
docker compose up --build      # mysql:8 + redis:7 + api (runs migrate + seed)
```

Set `DATABASE_URL=mysql+aiomysql://user:pass@host:3306/postit?charset=utf8mb4`.

## Paddle Billing (sandbox)
Billing endpoints return `503` until you set a Paddle API key. Create a free sandbox at
`sandbox-vendors.paddle.com` and, in `.env`:

```
PADDLE_API_KEY=pdl_sdbx_apikey_...
PADDLE_CLIENT_TOKEN=test_...
PADDLE_WEBHOOK_SECRET=pdl_ntfset_...
PADDLE_ENVIRONMENT=sandbox
```

Then admins create plans (which provision Paddle Products/Prices, annual price derived from the
discount %), users hit `POST /api/v1/billing/checkout` (returns a Paddle **transaction id** the
frontend opens with the Paddle.js overlay), and the webhook (`/api/v1/billing/webhook`,
`Paddle-Signature` HMAC-verified) syncs subscription/invoice state. Sandbox test card:
`4242 4242 4242 4242`, any future expiry / CVC. Paddle is a Merchant of Record — integrated over
its REST API with `httpx` (no SDK dependency).

## Architecture
`api (routers) → services (business logic) → repositories (data access) → models (ORM)`.
Cross-cutting: `schemas/` (Pydantic), `core/` (config, db, security, cache, rate-limit, deps).

```
app/
  core/            config, database, security, types, redis, cache, rate_limit, pagination, exceptions, deps
  models/          ORM models + enums + mixins
  schemas/         Pydantic request/response models
  repositories/    async data-access classes
  services/        business logic (auth, post, rewrite, billing, paddle_gateway, analytics, admin, …)
  api/v1/routes/   endpoint routers (+ routes/admin/* superuser API)
  db/seed.py       demo data
alembic/           migrations
tests/             pytest suite
```

## Tests
```bash
pytest
```

## Notes
- No scheduler yet: publishing marks targets published immediately and writes a `publish_jobs`
  outbox row — the durable contract a future worker will drain.
- Stored OAuth connection tokens are encrypted at rest (Fernet).
- Refresh tokens rotate and are reuse-detected; password change revokes all sessions.
