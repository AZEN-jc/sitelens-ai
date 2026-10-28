# SiteLens AI 验收记录

执行日期：2026-10-27。以下只记录本轮在当前工作区实际运行的检查。

## 2026-10-27 界面中文化与导航修复

| 检查 | 实际命令/操作 | 本轮结果 |
| --- | --- | --- |
| 设置入口回归测试（先红后绿） | `pnpm exec vitest run tests/App.test.ts --reporter=verbose`（在 `frontend` 目录） | 修改前按预期失败：主导航没有 `/settings` 链接；修改后通过。 |
| 前端测试 | `pnpm test`（在 `frontend` 目录） | 退出码 0；2 个测试通过。pnpm 提示当前 Node.js `v23.11.0` 不符合项目声明的支持版本范围。 |
| 前端类型检查与生产构建 | `pnpm build`（在 `frontend` 目录） | 退出码 0；`vue-tsc -b` 和 Vite 构建成功。图表分块 540.47 kB（gzip 188.56 kB），仍触发 500 kB 体积提示。 |
| 启动及 HTTP 冒烟 | `./scripts/start-local.sh`；`/usr/bin/curl` 请求 `/`、`/scans/1`、`/api/health` | 启动前浏览器遇到 `ERR_CONNECTION_REFUSED`；启动后首页和检测深链均返回 HTTP 200，健康接口返回 `{"status":"ok"}`。 |
| 浏览器界面验收 | 在本机首页点击主导航“设置” | 浏览器到达 `/settings`，显示中文设置表单、状态和密钥存储说明。仅验证桌面视口的实际导航与页面展示。 |
| HTML 报告中文回归测试（先红后绿） | `.venv/bin/pytest tests/backend/test_api.py::test_requires_authorization_and_escapes_report_html -q` | 修改前中文标题断言失败；修改后通过，同时保留 HTML 转义和 URL 查询参数脱敏断言。 |
| 后端测试与 lint | `.venv/bin/pytest -q && .venv/bin/ruff check backend tests` | 退出码 0；23 项测试通过，Ruff 全部通过。 |
| 重启后端及报告实测 | 重启 `./scripts/start-local.sh` 后请求 `/api/reports/1/export?format=html` | `/`、`/scans/1`、`/api/health` 均返回 HTTP 200；运行中导出报告包含中文标题“网站检测报告”和“公开响应证据”，不再包含英文报告标题。 |

## 结果

| 检查 | 实际命令/操作 | 本轮结果 |
| --- | --- | --- |
| 启动本机应用 | `./scripts/start-local.sh` | Uvicorn 在 `127.0.0.1:8000` 启动，进程保持运行。 |
| 页面/API 冒烟 | Python `urllib.request` 请求 `/`、`/scans/1`、`/api/health` | 三个路径均返回 HTTP 200；首页和深链返回 HTML，健康接口返回 `{"status":"ok"}`。这验证了服务可访问和 SPA 回退，不验证真实扫描提交。 |
| 后端测试 | `.venv/bin/pytest -q` | 退出码 0；23 passed in 2.64s。覆盖目标安全、采集/解析、规则匹配、API 持久化与比较、报告、AI 生命周期及两个受控站点夹具。 |
| 后端 lint | `.venv/bin/ruff check backend tests` | 退出码 0；All checks passed。 |
| 前端测试 | `pnpm --dir frontend test`，使用 Node 24.22.1 / pnpm 11.25.0 | 退出码 0；1 个测试文件、1 项测试通过。 |
| 前端类型检查与生产构建 | `pnpm --dir frontend build` | 退出码 0；`vue-tsc -b` 成功，Vite 转换 2248 个模块并构建完成。图表分块 540.47 kB（gzip 189.29 kB），触发 Vite 的 500 kB 提示；图表组件按需加载。 |

## 未执行与边界

- 没有对外部网站发起扫描。本机受控站点只在自动化测试中通过测试专用 resolver 替换访问；生产扫描器仍拒绝本机和私网目标。
- 没有调用真实 AI 服务；AI 行为由 mock 和本地测试服务覆盖。
- 没有自动执行浏览器视觉/无障碍检查或实际打印 PDF。
- 没有在本轮运行 `pnpm audit`；旧报告的审计结果不作为本轮结论。
- 该应用是无账号认证的本地单用户服务，只绑定回环地址。请勿暴露到共享网络。

## 答辩使用

演示前再次启动服务并运行关键测试。只有对自己拥有或获得明确授权的网站才能进行实时扫描；没有授权目标时，使用受控测试结果时必须标明是测试数据，而不是现场网站扫描结果。

## 2026-10-28 完整审查复验

| 检查 | 实际命令/操作 | 本轮结果 |
| --- | --- | --- |
| 初始服务检查 | `curl` 请求 `http://127.0.0.1:8000/`、`/scans/1`、`/api/health` | 启动前连接失败，curl 退出码 7；随后通过现有启动器启动服务。 |
| 启动本机应用 | `./scripts/start-local.sh` | Uvicorn 在 `127.0.0.1:8000` 启动并保持运行。 |
| 页面/API 冒烟 | curl 请求 `/`、`/scans/1`、`/settings`、`/api/health`、`/api/scans/1` 和设置页 JS 资源 | 全部 HTTP 200；健康接口返回 `{"status":"ok"}`；历史列表当前返回 1 条记录。页面路径检查只验证 SPA 响应，不等价于浏览器点击操作。 |
| 后端测试 | `./.venv/bin/pytest -q` | 退出码 0；23 passed in 4.85s。 |
| 后端 lint | `./.venv/bin/ruff check backend tests` | 退出码 0；All checks passed。 |
| 前端测试 | `pnpm --dir frontend test` | 退出码 0；2 个测试通过。pnpm 提示 Node.js v23.11.0 不符合 package.json 的支持版本范围。 |
| 前端类型检查与生产构建 | `pnpm --dir frontend build` | 退出码 0；`vue-tsc -b` 及 Vite 构建成功，转换 2248 个模块。`charts` 分块 540.47 kB（gzip 188.56 kB），触发 500 kB 提示。 |
| GitHub 回读 | Git remote 状态、GitHub 仓库元数据和 `main` commit API | 本地 `main` 与 `origin/main` 同步；远端仓库为私有；远端 main 指向 `27eb50547ef057c7c4263b5e390bf6f89bcf0f98`。Issue #1 可读取且包含先前学习材料。 |

本轮没有修改应用代码；审查发现和后续改进项见 [AUDIT_REPORT.md](AUDIT_REPORT.md)。未执行项及边界见该审查记录。

## 2026-10-28 历史分页修复与设置交互测试

| 检查 | 实际命令/操作 | 本轮结果 |
| --- | --- | --- |
| 历史分页回归（先红后绿） | `./.venv/bin/pytest tests/backend/test_api.py::test_scan_history_count_and_offset_reach_older_records -q` | 实现前按预期失败：`/api/scans/count` 被旧的 `/api/scans/{scan_id}` 路由当作 ID，返回 422；实现后退出码 0。测试建 35 条记录并验证总数、30+5 分页及无遗漏。 |
| 后端测试 | `./.venv/bin/pytest -q` | 退出码 0；24 passed in 5.07s。 |
| 后端 lint | `./.venv/bin/ruff check backend tests` | 退出码 0；All checks passed。 |
| 前端测试（Node.js 24.22.1） | `PATH=/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH /Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm --dir frontend test` | 退出码 0；5 个测试文件、5 项测试通过，覆盖导航、扫描授权提交、报告分页、比较分页和设置保存/测试失败/清除。Node 24.22.1 符合 `package.json` 声明范围。 |
| 前端类型检查与生产构建 | `PATH=/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH /Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm --dir frontend build` | 退出码 0；`vue-tsc -b` 通过，Vite 转换 2249 个模块并构建完成。图表分块 540.47 kB（gzip 189.29 kB），仍触发 500 kB 体积提示。 |
| 本机运行 | 重启 `./scripts/start-local.sh` 后用 curl 检查 | `/`、`/scans/1`、`/settings`、`/api/health` 均返回 HTTP 200；`/api/scans/count` 返回 1；`limit=1&offset=0` 返回 1 条，`offset=30` 返回 0 条；Uvicorn 监听 `127.0.0.1:8000`。 |

中间一次完整 lint 检查指出新导入顺序未排序；修正后再次运行后端测试与 Ruff，均通过。前端测试中测试替身最初把比较按钮和分页按钮选成同一个元素；调整测试选择器后，完整前端套件通过。该问题仅发生在测试替身中，未改动产品交互逻辑。

## 2026-10-28 依赖声明与 Python 发行包许可证

| 检查 | 实际命令/操作 | 本轮结果 |
| --- | --- | --- |
| 直接依赖元数据对照 | Python 读取 `.venv` 的 Python distribution metadata、前端 `node_modules` package manifest，与 `THIRD_PARTY_NOTICES.md` 对照 | 声明表所列直接依赖版本与包内声明许可证字段一致；193 个前端 package manifest 未发现 GPL 系列、unlicensed 或 undeclared 标记。此检查未访问上游许可证全文。 |
| Python wheel/sdist 构建 | `uv build --offline --out-dir /tmp/sitelens-license-fixed` | 退出码 0，离线构建 wheel 和 sdist；wheel 的 `METADATA` 包含 `License-Expression: GPL-3.0-or-later`；wheel 与 sdist 均包含 `LICENSE`。 |
| 锁文件一致性 | `uv lock --check --offline` | 退出码 0；依赖锁无需更新。 |
| 后端测试 | `./.venv/bin/pytest -q` | 退出码 0；24 passed in 8.44s。 |
| 后端 lint | `./.venv/bin/ruff check backend tests` | 退出码 0；All checks passed。 |

修改前对基线 wheel 的同一 SPDX 元数据断言按预期失败，证明原包元数据缺少许可证表达式；新增 `pyproject.toml` 声明后，离线构建和断言通过。

## 2026-10-29 Ponytail 最终审查与中文体验复验

| 检查 | 实际命令/操作 | 本轮结果 |
| --- | --- | --- |
| 后端测试 | `./.venv/bin/pytest -q` | 退出码 0；24 passed in 4.13s。 |
| 后端 lint | `./.venv/bin/ruff check backend tests` | 退出码 0；All checks passed。 |
| 前端测试（项目支持的 Node 24 runtime） | `PATH=/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH /Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm --dir frontend test` | 退出码 0；7 个测试文件、7 项测试全部通过，耗时 7.44s。包含导航、扫描授权、历史分页、设置交互、无效检测深链错误状态和类别中文映射。 |
| 前端类型检查与生产构建 | 同一 Node 24 runtime 下运行 `pnpm --dir frontend build` | 退出码 0；`vue-tsc -b` 与 Vite 构建成功，转换 2250 个模块，构建耗时 16.06s。`charts` 分块 540.47 kB（gzip 189.29 kB），仍有 Vite 500 kB 体积提示。 |
| diff 格式检查 | `git diff --check` | 退出码 0。 |
| 最新服务启动 | `./scripts/start-local.sh` 作为持续命令会话运行 | Uvicorn 使用当前后端和刚生成的前端 `dist`，监听 `127.0.0.1:8000`。 |
| 页面/API 直连冒烟 | Python `urllib.request` 使用 `ProxyHandler({})` 明确禁用环境代理后，请求 `/`、`/settings`、`/scans/999999`、`/api/health`、`/api/scans/999999`、`POST /api/scans`（未授权）、`/api/scans/count`、`/scans/1`、`/api/scans/1` 及 HTML/JSON 报告 | 首页、设置、两个 SPA 深链、健康、历史计数、历史详情及两种报告均得到预期 200；不存在记录返回 404 `未找到这条检测记录。`；未授权扫描返回 400 `请先确认你拥有该网站，或已获准分析其公开技术特征。`。没有发起新的外部扫描。 |
| 静态产物一致性 | 将运行中 `/` 响应字节与 `frontend/dist/index.html` 比较 | 完全一致：657 bytes，证明运行中服务使用本轮最新前端构建。 |

本轮中间一次使用默认 `urllib.request` 的冒烟受宿主环境 `HTTP_PROXY` / `HTTPS_PROXY` 影响，返回 502；当时环境没有 `NO_PROXY`。该返回不来自 SiteLens 应用。随后改为显式禁用代理并使用持续 Uvicorn 会话，完成上表直连复验。

### 本轮仍未执行

- 没有对新的外部网站发起扫描；历史记录中的 `scan #1` 仅用于读取现有结果与报告。
- 没有调用真实 AI 服务；AI 成功、失败、异常输出和密钥生命周期继续由自动化测试覆盖。
- 没有执行鼠标/键盘浏览器自动化、视觉回归、无障碍扫描或浏览器“打印为 PDF”。页面路径 HTTP 200 只能证明 SPA 路由可访问。
- 没有运行依赖漏洞数据库扫描，因此不声称第三方依赖不存在已知漏洞。
