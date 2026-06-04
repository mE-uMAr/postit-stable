#!/usr/bin/env bash
# Seed the database. Pass through flags: --core | --demo | --all (default: both).
#   scripts/seed.sh           # core + demo
#   scripts/seed.sh --core    # production-safe core only
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -d .venv ]; then
  # shellcheck disable=SC1091
  . .venv/bin/activate
fi

python -m app.db.seed "$@"
