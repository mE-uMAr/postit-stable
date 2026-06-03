#!/usr/bin/env bash
# One-command local backend bootstrap (SQLite, no Docker).
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
. .venv/bin/activate

pip install --upgrade pip >/dev/null
pip install -r requirements.txt

[ -f .env ] || cp .env.example .env

alembic upgrade head
python -m app.db.seed

echo
echo "Backend ready → http://localhost:8000/docs"
exec uvicorn app.main:app --reload --port 8000
