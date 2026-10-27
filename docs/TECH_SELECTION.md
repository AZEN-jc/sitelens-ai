# Phase 0: technology and license review

Reviewed through the public GitHub API on 2026-10-25. Repository activity is a point-in-time signal, not a guarantee of future maintenance.

| Project | Language | Repository license | Recent activity observed | Use in SiteLens |
| --- | --- | --- | --- | --- |
| [WhatWeb](https://github.com/urbanadventurer/WhatWeb) | Ruby | GPL-2.0; its README and license text say GPLv2, without “or later” | `pushed_at` 2026-04-02; not archived; reviewed commit `d279d93042d034f3fd29d5a893d44ccc0595d3f8` | README describes Ruby plugins, one-request stealth mode and more aggressive modes; plugin files were not copied |
| [HTTPArchive/wappalyzer](https://github.com/HTTPArchive/wappalyzer) | JavaScript | GPL-3.0 | `pushed_at` 2026-10-20; not archived; reviewed commit `bce5091d0ed2614a29c792436de1ac9080c3f51d` | README and `src/technologies` layout show a JavaScript detector and technology-data tree; no source or data copied |
| [wappalyzer-next](https://github.com/s0md3v/wappalyzer-next) | Python | GPL-3.0 | `pushed_at` 2026-09-30; not archived; reviewed commit `ff85c8b50485868a998f79f22e59d3cf1fe2f070` | README describes a Python package using Playwright/Chromium and Wappalyzer fingerprints; no source or data copied |

Repository-level license metadata does not establish the license of every rule, icon, fixture, or bundled dataset. The exact licensing of each upstream rule file was not established because no such files are being reused. The first-party fingerprint file in this project was written independently; no upstream rule data was imported. Before any future reuse, inspect the exact file, source revision, and its own licensing terms. Do not combine WhatWeb’s GPL-2.0-only code with GPL-3.0 code.

## Selected implementation

- Vue 3 + TypeScript + Vite for the local single-page UI; Element Plus for controls, Tailwind CSS for layout, ECharts for category distribution, and Vue Flow for clearly labeled inferred relationships.
- FastAPI + HTTPX/httpcore + BeautifulSoup for bounded HTTP collection and evidence extraction.
- A JSON fingerprint catalog with source-specific matching and inspectable evidence. Confidence weights are an internal score, not a probability.
- SQLite through SQLModel; startup `create_all` initializes the local schema. No migration framework is needed for this first schema.
- A user-configured OpenAI-compatible Chat Completions endpoint. API keys remain in memory only. HTML and JSON reports are generated locally; browser print styles provide PDF output without a server-side PDF dependency.

The selected stack supports a single local process for the built frontend and API. Playwright, queues, accounts, cloud deployment, and server-side PDF generation are excluded from the first release because they are not required for the core demonstration path.
