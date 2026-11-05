#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

# Why: 部分 IDE 注入的环境变量会干扰 Node 与 Python 子进程。
unset NODE_OPTIONS PYTHONPATH

if [ ! -x "$ROOT/.venv/bin/uvicorn" ]; then
  echo "缺少后端依赖，请先运行：uv sync --all-extras" >&2
  exit 1
fi
if [ ! -d "$ROOT/frontend/node_modules" ]; then
  echo "缺少前端依赖，请先运行：cd frontend && pnpm install --frozen-lockfile" >&2
  exit 1
fi
if [ ! -f "$ROOT/frontend/dist/index.html" ]; then
  (cd "$ROOT/frontend" && pnpm build)
fi

"$ROOT/.venv/bin/python" "$ROOT/scripts/seed-demo.py"

if command -v open >/dev/null 2>&1; then
  open "http://127.0.0.1:8000" 2>/dev/null || echo "请手动打开 http://127.0.0.1:8000" >&2
fi

exec "$ROOT/.venv/bin/uvicorn" app.main:app --app-dir "$ROOT/backend" --host 127.0.0.1 --port 8000
