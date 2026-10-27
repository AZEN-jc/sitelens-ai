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
