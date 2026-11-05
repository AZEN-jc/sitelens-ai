# Pstack Evidence Pack — SiteLens AI 交接取证

证据分级：`[实测 Measured]` 为本轮真实命令输出，`[推导 Inferred]` 为基于输出的归因。所有坐标均为 `file:start-end`。

## 目标实体

- 项目根：`/Users/admin/Documents/ChatGPT/New project`，即 Codex Desktop 的 "New project" 条目，界面显示名 "Lens AI 技术识别平台"。
- git：`960437a` on `main`，remote `https://github.com/AZEN-jc/sitelens-ai.git`，工作树有 2 个未提交改动 `[实测 Measured]`。
- 产品定义：`README.md:1-8`。安全与工程约束：`AGENTS.md:1-8`。
- 上轮审查结论：`docs/AUDIT_REPORT.md:1-88`。上轮验收声明：`docs/TEST_REPORT.md:1-101`。

## Step 1 复现记录（2026-11-04，Intel macOS，WorkBuddy 会话）

| # | 命令 | 实测输出 | 判定 |
|---|---|---|---|
| 1 | `./.venv/bin/pytest -q` | `24 passed in 4.99s` | 后端健康 |
| 2 | `./.venv/bin/ruff check backend tests` | `All checks passed!` | 后端健康 |
| 3 | `pnpm test`（默认 Node 22.22.2） | 7 errors、no tests、60.21s；`[vitest-pool]: Failed to start forks worker`、`Timeout waiting for worker to respond` | 前端验收链路断 |
| 4 | Node 24.22.1 + fallback pnpm | 2 passed + 5 errors、91.09s，同为 forks worker 超时 | 换 Node 版本无效 |
| 5 | `--pool=threads --maxWorkers=1 --fileParallelism=false` | 仍报 `Failed to start forks worker`、60.21s | 并发度不是根因 |
| 6 | `--pool=vmThreads --maxWorkers=2` | 6 passed / 1 failed、25.17s；`ReportsView.test.ts` 出现 `scans.length` undefined | 绕过进程池后能跑 |
| 7 | `node -e "fork(...)"` 用真实模块文件复测 | `FORK_OK pong`，去不去 `NODE_OPTIONS` 都成功 | 排除沙箱禁 fork |
| 8 | `env -u NODE_OPTIONS pnpm test` | **7 files / 8 tests 全过，4.28s，exit 0** | 根因锁定 |

## Step 2 根因剥离

- `NODE_OPTIONS=--require=<WorkBuddy Node language shim>` 由宿主注入，被 vitest 4 的 forks pool 继承到每个 worker；worker 内 shim 初始化与 broker 交互阻塞，60s 握手超时 `[推导 Inferred]`。
- 去掉该变量后默认 forks pool 4.28s 全绿，且 `ReportsView.test.ts` 通过，证明第 6 项的 `scans.length` 报错是 `vmThreads` 的 VM 上下文假象，不是产品缺陷 `[实测 Measured]`。
- 结论：**项目源码与测试没有坏**，`docs/TEST_REPORT.md` 的 "7 个测试文件通过" 在没有该注入的环境下成立。不能给项目打"修测试"补丁，那是修症状。
- 真正缺口：交付物缺少一条与宿主环境解耦的一键验收命令，且文档没有记录这个环境陷阱，导致换机器/换 IDE 后验收结果不可复现。

## 未提交改动（Codex 上一轮遗留，已由 #8 验证通过）

- `frontend/src/views/ScanView.vue:16-40`：AI 配置状态请求失败时不再吞掉已加载的检测结果，状态从 `boolean` 改为 `boolean | null` 三态。
- `frontend/tests/ScanView.test.ts:22-62`：新增对应回归用例，#8 中 2 tests passed。

## 追加复跑：第二处宿主注入（2026-11-04 23:18）

- 首次 `./scripts/verify-all.sh` 实跑退出码 1，后端 `20 passed, 4 errors`，4 个使用 `tmp_path` 的用例在 setup 阶段报 `FileExistsError: EEXIST`，路径位于 `/private/var/.../pytest-of-root` `[实测 Measured]`。
- 裸跑 `./.venv/bin/pytest -q` 稳定复现同样的 `20 passed, 4 errors`；`--basetemp=<独立目录>` 与 `env -u PYTHONPATH ./.venv/bin/pytest -q` 均为 `24 passed` `[实测 Measured]`。
- 根因：`PYTHONPATH` 注入的宿主 `sitecustomize.py` 代理了 `Path.mkdir`，临时根目录已存在时未正确处理 `exist_ok=True`，属于宿主 shim 缺陷 `[推导 Inferred]`。
- 处置：脚本改为同时 `unset NODE_OPTIONS PYTHONPATH`，直接清除注入，不改 pytest 配置与项目测试。
- 修正后 `./scripts/verify-all.sh` 退出码 0，后端 24 passed、Ruff 通过、前端 7 files / 8 tests、构建 2250 模块 `[实测 Measured]`。

## 门禁自身缺陷

- `pstack verify all` 在外部仓库会把 `node_modules` 一起扫：共 24638 个候选文件，其中 22921 个属依赖目录，进程被系统 SIGKILL `[实测 Measured]`。
- 已在 PSTACK_HOME 的 `scripts/verify-code-slop.py` 的 `collect_files` 加入依赖目录跳过集合，属于工作流工具修复，不改毕业设计源码。

## 2026-11-05 追加：首页图表预加载缺陷（实测推翻上轮审查结论）

- 复核 `frontend/dist/index.html` 发现首页带 `<link rel="modulepreload" href="/assets/charts-_pqqLW_Q.js">`，首屏预取 540.47 kB（gzip 189.29 kB）图表分块，而 `DashboardView` 不用 echarts。`docs/AUDIT_REPORT.md` 第 9 条"按结果页需要加载"的判断不成立 `[实测 Measured]`。
- 引用链测绘：`DashboardView`、`ReportsView`、`SettingsView`、`CompareView`、`useScanHistory` 的 chunk 全部反向 `from "./charts-_pqqLW_Q.js"`；该分块开头是 Vue 运行时代码，含 `createApp` 2 处、`echarts` 13 处 `[实测 Measured]`。
- 根因：`frontend/vite.config.ts` 的 `manualChunks` 强制把 echarts/zrender/vue-echarts 归到 `charts`，Rollup 把共享的 Vue 运行时也吸进同一分块，使所有页面必须依赖它。`TechnologyChart` 与 `ArchitectureGraph` 在 `frontend/src/views/ScanView.vue:10-11` 本就是 `defineAsyncComponent` 懒加载 `[推导 Inferred]`。
- 最小 diff：删除 `manualChunks` 整段，仅改 `frontend/vite.config.ts` 一个文件。
- 修复后 `dist/index.html` 的 `modulepreload` 数量为 0，首屏 gzip 260.59 kB 降到 102.86 kB（约减 60.5%）；最大 chunk 458.82 kB 低于 500 kB，Vite 警告消失。echarts 与 @vue-flow 分别落在两个懒加载分块 `[实测 Measured]`。
- `./scripts/verify-all.sh` 退出码 0；本机服务首页与 `dist/index.html` 字节一致，两个懒加载分块均返回 200，核心 API 与报告导出正常 `[实测 Measured]`。
- 未做真实浏览器图表渲染交互验收，不声称视觉表现已复验。此条已被 2026-11-05 晚的浏览器验收补齐。

## 2026-11-05 晚 四项未验收项取证（figure-it-out 剧本）

### 假说剪枝

- H1 四项都能自动补齐：证伪。无 playwright CLI、无 AI 环境变量、无授权公网目标、`backend/app/fetcher.py:111` 禁用代理 `[实测 Measured]`。
- H2 四项都做不到：证伪。本机有 Chrome 156、`registry.npmjs.org` 与 `pypi.org` 走 7890 均 200、Node 22 内置 WebSocket 可用 `[实测 Measured]`。
- H3 分项判定：采用。浏览器与漏洞库可自主完成，AI 与外扫受边界与网络约束。

### 浏览器（已完成）

- Chrome 156.0.8078.81 `--headless=new` + CDP 端口 9223 就绪。项目内无 playwright，改用 Node 内置 WebSocket 直连 CDP，零新增依赖 `[实测 Measured]`。
- CDP Fetch 拦截 `/api/scans/1` 返回受控 fixture（3 项技术），不写数据库。页面标题、4 个 tab、3 张技术卡片正常 `[实测 Measured]`。
- 首轮页面就绪即检查时 canvas 为 0，等待异步组件后为 1，尺寸 309×183，`toDataURL()` 长度 12610，证明 echarts 真实绘制 `[实测 Measured]`。
- 点击"架构推测"后 `.vue-flow__node` 4 个、SVG 9 个；`TechnologyChart` 分块仅在概览加载，`ArchitectureGraph` 的 JS/CSS 在切换后才请求，懒加载行为在真实浏览器里成立 `[实测 Measured]`。
- 脚本固化到 `scripts/verify-browser.cjs:1-30`，截图 88 KB。

### 依赖漏洞（已完成）

- `pnpm audit --json` 退出码 1，2 个 moderate：`glob` AbortSignal 取消绕过、`minimatch` globparts 放大 DoS `[实测 Measured]`。
- `uvx --from pip-audit pip-audit` 两次失败：宿主 `sitecustomize` 的 `Path.mkdir` EEXIST，以及 `ensurepip` SIGABRT。改用 OSV API 直连 `[实测 Measured]`。
- OSV `querybatch` 查 35 个 Python 包，命中 `pip 25.2`（GHSA-4xh5-x5gv-qwph 等）与 `pytest 8.4.2`（GHSA-6w46-j5rx-g56g、PYSEC-2026-1845），均为开发期工具 `[实测 Measured]`。

### 外部扫描（实测阻断）

- `POST /api/scans` 到 IANA 示例域名 `example.com` 带 `authorized=true`，连续 3 次均 504 `网站请求超时。`，每次 10.00s `[实测 Measured]`。
- 同机直连 curl 200 / 6.73s，走 7890 代理 200 / 0.35s；`GET /api/scans/count` 始终为 1，失败未落库 `[实测 Measured]`。
- 根因：`backend/app/fetcher.py:111` 的 `trust_env=False` 与 `backend/app/fetcher.py:100` 的 10 秒超时，叠加本机直连慢。`AGENTS.md:4` 禁止扫描路径启用环境代理，本轮未放宽 `[推导 Inferred]`。

### 真实 AI（边界已验，推理未完成）

- 本机无 Ollama、11434/8787 等端口无响应，`~/.codex/config.toml` 的 kimi 端点未启动；公网 provider 同样被 `trust_env=False` 挡住 `[实测 Measured]`。
- 用 `127.0.0.1:8788` 的 OpenAI 兼容测试替身验链路：配置 200、连接测试 `{"ok":true}`、状态不回传密钥、`confirm_data_sent=false` 返回 400、清除 204 后状态复位 `[实测 Measured]`。
- 该替身不是真实 LLM，没有调用 analyze 成功路径，避免假报告写入演示数据。真实模型推理仍缺一个本机可达端点 `[实测 Measured]`。
