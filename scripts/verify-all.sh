#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

# Why: 宿主注入 NODE_OPTIONS 会卡住 vitest worker，注入 PYTHONPATH 会让 pytest 临时目录报 EEXIST。
unset NODE_OPTIONS PYTHONPATH

if [ ! -x "$ROOT/.venv/bin/pytest" ]; then
  echo "缺少后端依赖，请先运行 .venv/bin/pip install -e '.[dev]'" >&2
  exit 1
fi
if [ ! -d "$ROOT/frontend/node_modules" ]; then
  echo "缺少前端依赖，请先运行 cd frontend && pnpm install --frozen-lockfile" >&2
  exit 1
fi

echo "== 后端测试 =="
(cd "$ROOT" && ./.venv/bin/pytest -q)
echo "== 后端静态检查 =="
(cd "$ROOT" && ./.venv/bin/ruff check backend tests)
echo "== 前端测试 =="
(cd "$ROOT/frontend" && pnpm test)
echo "== 前端生产构建 =="
(cd "$ROOT/frontend" && pnpm build)
echo "全部检查通过。"
