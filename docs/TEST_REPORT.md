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
| 前端测试（Node.js 24.22.1） | `pnpm --dir frontend test` | 退出码 0；5 个测试文件、5 项测试通过，覆盖导航、扫描授权提交、报告分页、比较分页和设置保存/测试失败/清除。Node 24.22.1 符合 `package.json` 声明范围。 |
| 前端类型检查与生产构建 | `pnpm --dir frontend build` | 退出码 0；`vue-tsc -b` 通过，Vite 转换 2249 个模块并构建完成。图表分块 540.47 kB（gzip 189.29 kB），仍触发 500 kB 体积提示。 |
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
| 前端测试（项目支持的 Node 24 runtime） | `pnpm --dir frontend test` | 退出码 0；7 个测试文件、7 项测试全部通过，耗时 7.44s。包含导航、扫描授权、历史分页、设置交互、无效检测深链错误状态和类别中文映射。 |
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

## 2026-11-04 交接复验与验收环境陷阱

本轮在 Intel macOS 的 WorkBuddy 会话中复验，只补齐一键验收入口与实测记录。后端、前端源码、vite 配置和现有测试均未改动。工作树两个未提交改动 `frontend/src/views/ScanView.vue` 与 `frontend/tests/ScanView.test.ts` 原样保留，经第 8 项验证通过。

下表按证据包第 1 至 8 项列出复现实验的真实命令与输出，失败项照实保留。

| 检查 | 实际命令/操作 | 本轮结果 |
| --- | --- | --- |
| 1 后端测试 | `./.venv/bin/pytest -q` | 退出码 0；`24 passed in 4.99s`。 |
| 2 后端 lint | `./.venv/bin/ruff check backend tests` | 退出码 0；`All checks passed!`。 |
| 3 前端测试（默认环境） | `pnpm test`（在 `frontend` 目录，Node 22.22.2） | 7 errors、no tests、60.21s；`Failed to start forks worker`、`Timeout waiting for worker to respond`。失败。 |
| 4 换 Node 版本 | Node 24.22.1 加 fallback pnpm 跑 `pnpm test` | 2 passed + 5 errors、91.09s，同为 forks worker 超时。失败。 |
| 5 降并发 | `pnpm test --pool=threads --maxWorkers=1 --fileParallelism=false` | 仍报 `Failed to start forks worker`、60.21s。失败。 |
| 6 换进程池 | `pnpm test --pool=vmThreads --maxWorkers=2` | 6 passed / 1 failed、25.17s；`ReportsView.test.ts` 出现 `scans.length` undefined。部分通过。 |
| 7 fork 能力复测 | `node -e "fork(...)"` 用真实模块文件 | `FORK_OK pong`，带不带 `NODE_OPTIONS` 都成功，排除沙箱禁 fork。 |
| 8 去除宿主注入 | `env -u NODE_OPTIONS pnpm test` | 7 files / 8 tests 全过，4.28s，退出码 0。 |

根因归属宿主环境注入。宿主把 `NODE_OPTIONS` 设为 `--require=<语言服务 shim>`，vitest 4 的 forks worker 继承该变量后初始化握手阻塞，60 秒后超时。第 7 项证明 fork 本身可用。第 8 项去掉该变量后默认 forks pool 全绿，`ReportsView.test.ts` 也通过，说明第 6 项的 `scans.length` 报错属于 vmThreads 上下文假象，不是产品缺陷。第 3 至 6 项的失败都不来自项目源码。

一键脚本本轮实跑 `./scripts/verify-all.sh`。脚本开头清除宿主注入的 `NODE_OPTIONS` 与 `PYTHONPATH`，四步顺序执行，`set -eu` 保证任一步失败立即停止。摘录的真实输出如下。

```text
$ ./scripts/verify-all.sh
== 后端测试 ==
........................                                                 [100%]
24 passed in 3.01s
== 后端静态检查 ==
All checks passed!
== 前端测试 ==
 Test Files  7 passed (7)
      Tests  8 passed (8)
   Duration  4.44s (transform 2.14s, setup 0ms, import 9.10s, tests 857ms, environment 10.99s)
== 前端生产构建 ==
✓ 2250 modules transformed.
dist/assets/charts-_pqqLW_Q.js             540.47 kB │ gzip: 189.29 kB
✓ built in 12.21s
全部检查通过。
```

脚本整体退出码 0。后端 24 passed，前端 7 个测试文件、8 项测试通过，`vue-tsc -b` 与 Vite 构建成功，转换 2250 个模块。`charts` 分块 540.47 kB（gzip 189.29 kB）仍触发 Vite 的 500 kB 提示。前端测试 stderr 出现 `Failed to resolve component: el-button` 的 Vue 警告，不影响断言结果。上述数字来自本轮脚本实跑，与表中证据包数字分属不同次运行。

复跑中发现第二处宿主注入干扰。`PYTHONPATH` 指向宿主文件代理 shim，pytest 的 `tmp_path` 夹具在临时根目录已存在时会收到 `EEXIST`，表现为 4 个用例在 setup 阶段报错。裸跑 `./.venv/bin/pytest -q` 复现为 `20 passed, 4 errors`；`env -u PYTHONPATH ./.venv/bin/pytest -q` 与 `pytest -q --basetemp=<独立目录>` 均回到 `24 passed`。脚本选择清除注入变量，不改动项目测试配置。

### 本机服务端到端冒烟

用 `env -u PYTHONPATH -u NODE_OPTIONS ./scripts/start-local.sh` 启动服务。全部请求显式禁用代理，没有对外部网站发起扫描。

| 检查 | 实际命令/操作 | 本轮结果 |
| --- | --- | --- |
| 健康检查 | `GET /api/health` | 200 `{"status":"ok"}`。 |
| 页面与深链 | `GET /`、`/settings`、`/scans/1`、`/scans/999999` | 均 200，657 bytes。 |
| 静态产物一致性 | 比较运行中 `/` 与 `frontend/dist/index.html` | 字节完全一致。 |
| 历史与证据 | `/api/scans/count`、`/api/scans/1`、`/api/scans?limit=1&offset=0`、`/api/scans/1/evidence` | 均 200，总数为 1。 |
| 不存在记录 | `GET /api/scans/999999` | 404 `未找到这条检测记录。`。 |
| 报告导出 | `format=html` 与 `format=json` | 200，HTML 854 bytes，JSON 3081 bytes。 |
| 授权门禁 | `POST /api/scans` 且 `authorized=false` | 400 `请先确认你拥有该网站，或已获准分析其公开技术特征。`。 |
| 私网拦截 | `POST /api/scans` 目标为本机地址且 `authorized=true` | 400 `禁止检测解析到私网、本机或保留地址的目标。`，未发起请求。 |
| AI 配置状态 | `GET /api/ai/config` | 200 `{"configured":false,"base_url":null,"model":null}`，未回传密钥。 |

### 本轮未执行

- 没有对真实外部网站发起扫描。
- 没有调用真实 AI 服务。
- 没有执行浏览器自动化、视觉回归、无障碍扫描或打印 PDF。
- 没有运行依赖漏洞数据库扫描，因此不声称第三方依赖不存在已知漏洞。

## 2026-11-05 首页图表预加载修复

复核 `frontend/dist/index.html` 时发现首页带 `modulepreload` 指向 540.47 kB 的图表分块，与 `docs/AUDIT_REPORT.md` 第 9 条"按结果页需要加载"的判断不符。该条已改写，本节记录修复与实测。

| 检查 | 实际命令/操作 | 本轮结果 |
| --- | --- | --- |
| 修复前基线 | 读取 `frontend/dist/index.html` 与 chunk 清单 | 首页 `modulepreload` 指向 `charts-_pqqLW_Q.js` 528K（gzip 189.29 kB），入口 195K（gzip 71.30 kB），首屏 gzip 合计 260.59 kB。 |
| 引用链测绘 | 检索各页面 chunk 的 import 目标 | `DashboardView`、`ReportsView`、`SettingsView`、`CompareView`、`useScanHistory` 全部反向 import charts 分块，说明共享依赖被吸入。 |
| 根因 | 读 `frontend/vite.config.ts` 的 `manualChunks` 与 `frontend/src/views/ScanView.vue:10-11` | 图表组件本已是 `defineAsyncComponent` 懒加载，强制分块让 Vue 运行时落入 charts，破坏了按需加载。 |
| 最小 diff | 删除 `manualChunks` 整段，仅改 1 个文件 | `pnpm build` 退出码 0，2250 模块转换成功。 |
| 修复后首页 | 读取新 `dist/index.html` | `modulepreload` 数量为 0，只有入口 `index-BtIZbM6D.js` 281.03 kB（gzip 102.86 kB）。 |
| 首屏体积 | 对比前后 gzip 合计 | 260.59 kB 降到 102.86 kB，减少约 60.5%。 |
| 分块归属 | 读取新 chunk 清单 | echarts 落到 `TechnologyChart-DWkLxSGD.js` 458.82 kB（gzip 157.39 kB），@vue-flow 落到 `ArchitectureGraph-C2UOQ4-C.js` 163.64 kB，均为懒加载。最大分块低于 500 kB，Vite 体积提示消失。 |
| 全量验收 | `./scripts/verify-all.sh` | 退出码 0，后端 24 passed、Ruff 通过、前端 7 files / 8 tests、构建成功。 |
| 运行复验 | 启动本机服务后请求 `/` 与两个懒加载分块 | 首页字节与 `dist/index.html` 一致，两个分块均 200，核心 API 与 HTML 报告均 200。 |

修复只删除构建配置中的手动分块规则，没有改动任何业务组件、接口或数据结构。浏览器图表验收已在下一节补齐。

## 2026-11-05 晚 四项未验收项补齐

按 pstack 的 figure-it-out 剧本执行。先证伪"四项都能自动补齐"与"四项都做不到"两个极端假说，再分项取证。全程没有放宽 `AGENTS.md` 的安全约束。

### 1 真实浏览器图表渲染交互验收（已完成）

本机 Chrome 156.0.8078.81 以 `--headless=new` 启动 CDP 端口 9223。用 CDP `Fetch.fulfillRequest` 拦截 `/api/scans/1` 返回受控 fixture（3 项技术、3 类证据），没有写数据库，没有改业务源码。验收方法记录在本节。

| 检查 | 实际命令/操作 | 本轮结果 |
| --- | --- | --- |
| 页面渲染 | CDP `Page.navigate` 到 `/scans/1` | 标题、受控样本 h1、4 个分区按钮（概览/证据/架构推测/AI 分析）、3 张技术卡片全部出现。 |
| 图表画布 | 等待异步组件后读取 `.side-panel canvas` | canvas 数量 1，尺寸 309×183，`toDataURL()` 长度 12610，证明 echarts 真实绘制了像素，不是空容器。 |
| 首次加载时机 | 页面就绪后立刻读取 | canvas 数量 0，`TechnologyChart-DWkLxSGD.js` 已请求。图表是异步组件，需等待渲染，首轮检查的 0 不是缺陷。 |
| 交互切换 | 点击"架构推测"按钮并等待 | `.vue-flow__node` 4 个、SVG 9 个、方法说明可见。 |
| 懒加载实证 | `performance.getEntriesByType('resource')` | 概览只加载 `TechnologyChart` 分块，切到架构后才出现 `ArchitectureGraph` 的 JS 与 CSS 分块。 |
| 视觉留证 | `Page.captureScreenshot` | 生成 88 KB PNG 截图。 |

最小心智模型：

```text
Chrome 156 headless (CDP :9223)
  | Page.navigate /scans/1
  v
SiteLens SPA -- GET /api/scans/1 --> CDP Fetch 拦截
  |                                    |
  | <-- 受控 fixture (3 项技术) --------+
  v
defineAsyncComponent
  +-- TechnologyChart 懒加载 --> canvas 309x183
  +-- ArchitectureGraph 懒加载 --> 4 node / 9 svg
```

### 2 依赖漏洞数据库扫描（已完成，问题如实保留）

| 检查 | 实际命令/操作 | 本轮结果 |
| --- | --- | --- |
| 前端 | `pnpm audit --json`（走 7890 代理） | 退出码 1，2 个 moderate：`glob` 的 AbortSignal 取消绕过、`minimatch` 的 globparts 放大 DoS。 |
| Python 工具链 | `uvx --from pip-audit pip-audit -r ...` | 两次失败。第一次撞宿主 `sitecustomize` 的 `Path.mkdir` EEXIST，第二次 `ensurepip` SIGABRT。工具本身跑不起来，换直连 OSV API。 |
| Python 依赖 | 对 `uv pip freeze` 导出的 35 个包批量 POST `https://api.osv.dev/v1/querybatch` | 2 个包命中公告：`pip 25.2`（GHSA-4xh5-x5gv-qwph 等）、`pytest 8.4.2`（GHSA-6w46-j5rx-g56g、PYSEC-2026-1845）。两者都是开发期工具，不在运行时业务依赖里。 |

没有升级任何依赖，也没有把警告改掉。结论只能写成"已完成数据库比对并发现 4 处公告"，不能写成"依赖无漏洞"。

### 3 外部网站扫描（已实测，链路被安全约束阻断）

用户授权本轮演示，目标取 IANA 保留的示例域名 `example.com`，只发普通 GET，不做任何漏洞探测。

| 检查 | 实际命令/操作 | 本轮结果 |
| --- | --- | --- |
| 扫描器链路 | `POST /api/scans` 带 `authorized=true`，连续 3 次 | 每次均 `504 {"detail":"网站请求超时。"}`，耗时 10.00 秒，稳定复现。 |
| 直连对照 | `curl --noproxy '*' https://example.com` | 200，耗时 6.73 秒。 |
| 代理对照 | `curl -x http://127.0.0.1:7890 https://example.com` | 200，耗时 0.35 秒。 |
| 失败边界 | `GET /api/scans/count` | 始终为 1，超时请求没有落库，没有污染历史。 |

根因是 `backend/app/fetcher.py:111` 的 `trust_env=False` 加上 `backend/app/fetcher.py:100` 的 10 秒超时。本机直连慢、代理快，但 `AGENTS.md:4` 明确禁止扫描路径启用环境代理，这是防 SSRF 的硬边界。本轮不为跑通验收而放宽它。结论：外部扫描链路当前不可完成，需要一台能直连公网且延迟低于 10 秒的机器，或由部署方在隔离网络内自行评估。

### 4 真实 AI 服务（边界已验，真实模型推理未完成）

本机没有 Ollama、没有运行中的 OpenAI 兼容端点（11434、8787 等端口均无响应），`~/.codex/config.toml` 里的 kimi 端点 8787 未启动。公网 provider 同样被 `trust_env=False` 挡住。因此用本机 `127.0.0.1:8788` 的 OpenAI 兼容测试替身验证链路边界，**不把它称为真实 AI 推理**。

| 检查 | 实际命令/操作 | 本轮结果 |
| --- | --- | --- |
| 配置 | `POST /api/ai/config` 写入 base_url、密钥、模型 | 200，返回 `configured:true`，不回显密钥。 |
| 连接 | `POST /api/ai/test` | 200 `{"ok":true}`，后端真实发出一次 HTTP 请求到本机替身。 |
| 密钥边界 | `GET /api/ai/config` | 只返回 `configured`、`base_url`、`model`，密钥未出现。 |
| 确认门禁 | `POST /api/ai/analyze` 且 `confirm_data_sent=false` | 400 `请先确认页面展示的分析数据，再发送到 AI 服务。` |
| 清除 | `DELETE /api/ai/config` | 204，随后状态复位为 `configured:false`。 |

没有调用 `analyze` 的成功路径，避免把测试替身生成的假报告写进演示数据。真实模型推理仍需提供一个本机可达的 OpenAI 兼容端点（例如启动 Ollama 并用 `http://127.0.0.1:11434/v1`），或由部署方自行接入。AI 成功、失败、异常输出与密钥生命周期的自动化覆盖仍由现有后端测试承担。

### 本轮仍未执行

- 真实 LLM 推理与真实 AI 报告落库，原因是本机没有可用模型端点。
- 对公网目标的完整成功扫描，原因是扫描器禁用代理且 10 秒超时。
- 浏览器视觉回归、无障碍扫描、打印 PDF，以及鼠标 hover 触发的 echarts tooltip 细节。
- 依据漏洞公告升级依赖或做修复验证，本轮只做比对与记录。
