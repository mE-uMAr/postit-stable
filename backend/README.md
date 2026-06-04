# Postit API (FastAPI)

Async, production-grade backend for Postit: auth (+ password reset), workspaces & RBAC, social
connections, posts + a **pluggable AI** rewrite engine, a **real scheduled-publish worker**,
analytics with AI best-time suggestions, Paddle billing with admin-managed plans, notifications,
brand voice, an **admin-editable site CMS**, **DB error logging**, and a superuser admin API.

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
python -m app.db.seed --all              # core (platforms/plans/site/superadmin) + demo
uvicorn app.main:app --reload --port 8000
```

Or just `scripts/dev.sh` (venv + deps + migrate + seed + run). Seeding is split:

```bash
python -m app.db.seed --core   # production bootstrap: platforms, plans, site content, superadmin
python -m app.db.seed --demo   # the "Maple & Co" sample workspace
python -m app.db.seed --all    # both (default when no flag)
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

## Pluggable AI (generation)
The rewrite engine is provider-agnostic (`app/services/ai/`). It ships with a deterministic
offline **mock** (default) and thin `httpx` adapters for **Anthropic, OpenAI, Groq, and Gemini**.
Point it at any model via env — any failure (no key, network, provider outage) degrades gracefully
back to the mock so generation never hard-fails:

```
AI_PROVIDER=anthropic        # mock | anthropic | openai | groq | gemini
AI_API_KEY=sk-ant-...
AI_MODEL=claude-sonnet-4-6   # optional; sensible per-provider default otherwise
AI_BASE_URL=                 # optional; for self-hosted / OpenAI-compatible gateways
```
Add a provider by implementing `LLMProvider.generate` and registering it in `ai/registry.py`.
`GET /readyz` reports the active provider.

## Scheduled publishing (worker)
Scheduling a post enqueues a `publish_jobs` outbox row (`run_after = scheduled_at`). An in-process
asyncio worker (`app/worker/scheduler.py`, started in the app lifespan) claims due jobs atomically
and publishes via `services/publish.py`, with bounded retries + backoff. Toggle with
`SCHEDULER_ENABLED`. **When running multiple web workers, enable it on exactly one** (or run a
dedicated process) to avoid double-processing.

## Site CMS + error logging
- Superusers edit the public marketing site (hero, features, testimonials, FAQ, pricing toggle,
  flags) via `GET/PUT /api/v1/admin/site`; the landing reads `GET /api/v1/site/content` (cached).
- Unhandled/5xx errors are persisted to `error_logs` (best-effort, isolated session) and surfaced
  at `GET /api/v1/admin/errors`.

## Architecture
`api (routers) → services (business logic) → repositories (data access) → models (ORM)`.
Cross-cutting: `schemas/` (Pydantic), `core/` (config, db, security, cache, rate-limit, deps).

```
app/
  core/            config, database, security, types, redis, cache, rate_limit, pagination, exceptions, deps
  models/          ORM models + enums + mixins (incl. error_log, site_setting)
  schemas/         Pydantic request/response models
  repositories/    async data-access classes
  services/        business logic (auth, post, publish, rewrite, billing, analytics, admin, site, …)
    ai/            pluggable LLM provider module (base, registry, service, providers/*)
  worker/          in-process scheduler that drains the publish outbox
  api/v1/routes/   endpoint routers (+ routes/admin/* superuser API)
  db/seed.py       core + demo seeding (CLI: --core/--demo/--all)
alembic/           migrations (0001 baseline, 0002 error_logs + site_settings)
tests/             pytest suite
```

## Tests
```bash
pytest
```

## Notes
- Scheduled posts are published by the in-process worker draining the `publish_jobs` outbox at
  `run_after`; immediate publish runs synchronously. Platform calls are mocked (no live social APIs).
- Plan limits are enforced (AI generations, connections, seats); post edits use optimistic
  concurrency (`version` → `409 stale_version`).
- Stored OAuth connection tokens are encrypted at rest (Fernet).
- Refresh tokens rotate and are reuse-detected (and carry `is_superuser` for edge gating); password
  change and reset revoke all sessions.
- `is_superuser` is the platform-admin boundary; workspace roles (owner/admin/editor/viewer) gate
  in-workspace actions via `require_workspace_role`.
