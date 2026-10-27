# SiteLens AI

SiteLens AI analyzes public website technology signals for sites you own or are authorized to inspect. Each detection includes the observed evidence behind it. AI analysis explains those results; it does not decide whether a technology is present.

## Requirements

- Python 3.11 or newer
- Node.js 22.22.2 or newer in the 22.x line, or 24.15.0 or newer
- pnpm 11

## Run locally

```sh
uv sync --all-extras
cd frontend
pnpm install --frozen-lockfile
pnpm build
cd ..
./scripts/start-local.sh
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The server binds only to loopback. The SQLite history is created at `data/sitelens.sqlite`.

If you do not use uv, create `.venv` with Python and install the project using `.venv/bin/pip install -e '.[dev]'`; `uv.lock` records the verified Python dependency resolution.

For frontend development, keep the API running in one terminal:

```sh
.venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Then start Vite in another terminal:

```sh
cd frontend
pnpm dev
```

## Use

1. Enter an HTTP(S) URL and confirm that you own the site or have permission to analyze it.
2. Review technology cards and their matching response evidence.
3. Optionally configure an OpenAI-compatible Chat Completions endpoint in Settings. The API key stays in backend memory until restart.
4. Before generating AI analysis, review the exact structured summary shown by the page and confirm sending it to the configured service.
5. Compare saved scans and export HTML or JSON. In the HTML report, use the browser’s **Print → Save as PDF** action for a PDF copy.

The scanner performs ordinary public HTTP GET requests only. It blocks local, private, and reserved addresses, rechecks every redirect, pins connections to the validated DNS address, uses a 10-second timeout, allows at most five redirects, and reads at most 5 MiB. It does not probe vulnerabilities or bypass access controls. The authorization checkbox is a user attestation; the software cannot independently verify ownership.

Configuring a local or private AI Base URL is an explicit trust decision and is separate from scanning: the scanner still blocks private targets. Do not expose this single-user local service on a shared network; it has no user authentication.

## Verification

```sh
.venv/bin/pytest
.venv/bin/ruff check backend tests
cd frontend && pnpm test && pnpm build
```

## 中文学习与答辩材料

- [学习手册：模块地图、扫描链路、安全边界、自测题](docs/LEARNING_GUIDE.md)
- [5–8 分钟答辩稿、演示步骤与常见问题](docs/DEFENSE_SCRIPT.md)
- [AI 辅助使用记录](docs/AI_USAGE_LOG.md)
- [最新验证记录](docs/TEST_REPORT.md)

Phase 0 findings and third-party license boundaries are in [docs/TECH_SELECTION.md](docs/TECH_SELECTION.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Architecture and API details are in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/API.md](docs/API.md).
