#!/usr/bin/env bash
# One-command local backend bootstrap (SQLite).
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -qr requirements.txt
fi
# shellcheck disable=SC1091
. .venv/bin/activate

[ -f .env ] || cp .env.example .env

alembic upgrade head
python -m app.db.seed --all   # core + demo workspace for local dev

echo "Backend ready → http://localhost:8000/docs"
exec uvicorn app.main:app --reload --port 8000
