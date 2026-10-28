# 第三方来源与许可证声明

SiteLens AI 项目采用 `GPL-3.0-or-later`。本项目没有复制 WhatWeb、HTTPArchive/wappalyzer 或 wappalyzer-next 的源码和指纹数据；`backend/fingerprints/technologies.json` 为本项目自行编写的规则文件。

## 参考项目

这些项目只用于方案调研。表中的 commit 是本项目做 Phase 0 核对时查看的具体版本，用于说明当时依据；它们没有作为代码依赖或数据依赖进入 SiteLens AI。

| 项目 | 核对版本 | 仓库许可证 | 在本项目中的复用/修改情况 | 来源 |
| --- | --- | --- | --- | --- |
| WhatWeb | `d279d93042d034f3fd29d5a893d44ccc0595d3f8` | GPL-2.0 only | 无代码/插件/指纹复制，无修改；仅参考公开技术识别思路 | [urbanadventurer/WhatWeb](https://github.com/urbanadventurer/WhatWeb) |
| HTTPArchive/wappalyzer | `bce5091d0ed2614a29c792436de1ac9080c3f51d` | GPL-3.0 | 无源码/指纹数据复制，无修改；仅参考检测器与技术数据组织思路 | [HTTPArchive/wappalyzer](https://github.com/HTTPArchive/wappalyzer) |
| wappalyzer-next | `ff85c8b50485868a998f79f22e59d3cf1fe2f070` | GPL-3.0 | 无源码/指纹数据复制，无修改；仅参考 Python/浏览器识别方向 | [s0md3v/wappalyzer-next](https://github.com/s0md3v/wappalyzer-next) |

仓库许可证不自动等于每个规则、图标、fixture 或数据文件的许可证。本项目当前没有导入任何上游指纹规则，因此不存在“已导入规则文件”的单独授权结论。未来若引入上游规则，必须逐文件核对具体来源版本、授权条款及与本项目发行许可证的兼容性后再纳入。WhatWeb 的 GPL-2.0-only 代码不能直接与 GPL-3.0 代码合并发布。

## 直接 Python 依赖

下表版本与声明许可证字段在 2026-10-28 通过当前本机安装包元数据核对。项目没有修改这些第三方包。

| 包 | 版本 | 许可证 | 修改情况 | 来源 |
| --- | ---: | --- | --- | --- |
| FastAPI | 0.162.0 | MIT | 未修改 | [fastapi/fastapi](https://github.com/fastapi/fastapi) |
| HTTPX | 0.28.1 | BSD-3-Clause | 未修改 | [encode/httpx](https://github.com/encode/httpx) |
| httpcore | 1.0.9 | BSD-3-Clause | 未修改 | [encode/httpcore](https://github.com/encode/httpcore) |
| Beautiful Soup | 4.15.0 | MIT | 未修改 | [facelessuser/beautifulsoup4](https://git.launchpad.net/beautifulsoup) |
| SQLModel | 0.0.48 | MIT | 未修改 | [fastapi/sqlmodel](https://github.com/fastapi/sqlmodel) |
| Uvicorn | 0.54.0 | BSD-3-Clause | 未修改 | [encode/uvicorn](https://github.com/encode/uvicorn) |
| SQLAlchemy | 2.1.6 | MIT | 未修改 | [sqlalchemy/sqlalchemy](https://github.com/sqlalchemy/sqlalchemy) |
| pytest | 8.4.2 | MIT | 未修改 | [pytest-dev/pytest](https://github.com/pytest-dev/pytest) |
| pytest-asyncio | 1.4.0 | Apache-2.0 | 未修改 | [pytest-dev/pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) |
| Ruff | 0.17.2 | MIT | 未修改 | [astral-sh/ruff](https://github.com/astral-sh/ruff) |

## 直接前端依赖

| 包 | 版本 | 许可证 | 修改情况 | 来源 |
| --- | ---: | --- | --- | --- |
| Vue | 3.5.44 | MIT | 未修改 | [vuejs/core](https://github.com/vuejs/core) |
| Vue Router | 4.6.4 | MIT | 未修改 | [vuejs/router](https://github.com/vuejs/router) |
| Element Plus | 2.14.7 | MIT | 未修改 | [element-plus/element-plus](https://github.com/element-plus/element-plus) |
| Tailwind CSS | 4.3.3 | MIT | 未修改 | [tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) |
| @tailwindcss/vite | 4.3.3 | MIT | 未修改 | [tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) |
| @vitejs/plugin-vue | 6.0.10 | MIT | 未修改 | [vitejs/vite-plugin-vue](https://github.com/vitejs/vite-plugin-vue) |
| Vite | 7.3.7 | MIT | 未修改 | [vitejs/vite](https://github.com/vitejs/vite) |
| ECharts | 6.1.0 | Apache-2.0 | 未修改 | [apache/echarts](https://github.com/apache/echarts) |
| vue-echarts | 8.3.2 | MIT | 未修改 | [ecomfe/vue-echarts](https://github.com/ecomfe/vue-echarts) |
| Vue Flow core / background / controls | 1.48.2 / 1.3.2 / 1.1.3 | MIT | 未修改 | [bcakmakoglu/vue-flow](https://github.com/bcakmakoglu/vue-flow) |
| TypeScript | 5.9.3 | Apache-2.0 | 未修改 | [microsoft/TypeScript](https://github.com/microsoft/TypeScript) |
| Vitest | 4.1.12 | MIT | 未修改 | [vitest-dev/vitest](https://github.com/vitest-dev/vitest) |
| Vue Test Utils | 2.5.1 | MIT | 未修改 | [vuejs/test-utils](https://github.com/vuejs/test-utils) |
| jsdom | 27.4.0 | MIT | 未修改 | [jsdom/jsdom](https://github.com/jsdom/jsdom) |
| vue-tsc | 3.3.13 | MIT | 未修改 | [vuejs/language-tools](https://github.com/vuejs/language-tools) |

本机曾对 193 个已安装前端 package manifest 做许可证字段扫描，当时没有发现 GPL-family、unlicensed 或 undeclared 标记。该检查只能说明包元数据状态，不能替代上游许可证全文核验。依赖升级后应重新生成清单，并在发行包中保留适用的许可证文本和 notices。
