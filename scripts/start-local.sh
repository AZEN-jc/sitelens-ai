#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ ! -x "$ROOT/.venv/bin/uvicorn" ]; then
  echo "Backend dependencies are missing. Run: python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'" >&2
  exit 1
fi
if [ ! -f "$ROOT/frontend/dist/index.html" ]; then
  echo "Frontend is not built. Run: cd frontend && pnpm install --frozen-lockfile && pnpm build" >&2
  exit 1
fi
exec "$ROOT/.venv/bin/uvicorn" app.main:app --app-dir "$ROOT/backend" --host 127.0.0.1 --port 8000
