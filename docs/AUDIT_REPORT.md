# SiteLens AI Ponytail 完整审查记录

**What this repo does:** SiteLens AI 是一个本机单用户的网站技术特征识别与分析工具。它对用户声明获准分析的公网 HTTP(S) 目标做普通 GET，依据公开响应和项目自编写指纹给出带证据的技术识别结果，并提供历史、报告和可选 AI 解释。本文按毕业设计演示负载审查：单机、低并发，不按公网多用户服务评估容量。

审查日期：2026-10-28 至 2026-10-29。审查对象为当前 `main` 工作树，目标场景是本机单用户毕业设计演示。审查覆盖 Vue 页面与路由、FastAPI、URL/DNS 安全、固定 IP 请求、响应解析、指纹规则、SQLite、历史比较、报告、AI、安全配置、启动/构建、测试与学生文档。

本记录按 Ponytail 的优先级给出已复现问题和剩余事项。每个“已修复”项都要求有可复现行为、代码修改和对应验证；没有把静态猜测当成已确认缺陷。

## Must fix

### 1. 中文界面仍会直接显示英文后端错误 — 已修复

**复现方式**：提交未勾选授权的检测、读取不存在的检测记录、AI 未配置时测试/分析，或触发 URL/网络限制时，FastAPI 原先返回英文 `detail`；`frontend/src/api.ts` 的兜底错误也为英文。这些文本会直接出现在中文界面的 Element Plus 消息中。

**修复**：`backend/app/security.py`、`fetcher.py`、`ai_service.py`、`main.py` 的用户可见错误统一改为中文；前端请求失败兜底改为中文。异常类型、HTTP 状态码和安全判断没有放宽。

**验证**：后端测试新增授权错误中文断言，完整 pytest 与 Ruff 通过；最终运行验收直接请求不存在记录和未授权提交，确认服务返回中文信息。

### 2. 不存在的检测深链会落到空白内容区 — 已修复

**复现方式**：直接进入 `/scans/999999`。原组件捕获 API 失败后只弹一次消息，`scan` 仍为空，页面主体没有稳定错误状态，用户会感觉“页面什么都没有”。

**修复**：`ScanView.vue` 增加 `loadError`，失败时明确显示“无法显示这条检测记录”、具体错误和“返回概览”入口；切换检测 ID 时会重置旧数据和错误状态。

**验证**：新增 `frontend/tests/ScanView.test.ts`，覆盖不存在记录的可见错误状态和返回入口；完整前端测试通过。

## Should fix

### 3. 识别类别仍以英文出现在中文结果页 — 已修复

**复现方式**：指纹规则保留规范英文类别，例如 `Web server`、`Frontend framework`。结果卡片、证据标题和类别图直接显示原字段，造成中文界面混杂英文。

**修复**：新增 `frontend/src/labels.ts`，集中把已知规范类别映射为中文，未知类别原样保留，避免未来扩展规则时页面变空。结果卡片、证据区和图表统一使用映射。

**验证**：`frontend/tests/labels.test.ts` 覆盖已知类别和未知类别回退；完整前端测试与生产构建通过。

### 4. HTML 报告仍暴露英文类别 — 已修复

**复现方式**：导出包含 `Web server` 技术的 HTML 报告，报告正文原先输出 `类别：Web server`。

**修复**：后端报告导出使用与前端含义一致的中文类别表，未知类别仍保留原值。

**验证**：`tests/backend/test_api.py` 明确断言报告包含 `类别：Web 服务器` 且不包含 `类别：Web server`，同时继续验证 HTML 转义和 URL 查询参数脱敏。

### 5. 历史超过 30 条后无法继续选择 — 已修复

原 `/api/scans` 只返回最近 30 条，比较和报告页面没有加载更多入口。现已增加 `limit` / `offset`、`/api/scans/count`，前端比较与报告页面可以继续加载旧记录，首页总数使用真实计数。

回归测试创建 35 条本地记录，验证总数 35、第一页 30、第二页 5，且两页覆盖全部 ID。

### 6. 设置页关键操作缺少组件级回归 — 已补齐

设置页测试现在驱动保存配置、保存后密钥输入清空、连接失败提示、清除配置和状态刷新。它覆盖 Vue 组件与 API 边界；没有把“页面能返回 HTML”当成按钮交互已经验证。

### 7. Python 发行包元数据缺少 SPDX 许可证表达式 — 已修复

项目已有 GPL-3.0-or-later `LICENSE`，但旧 `pyproject.toml` 没有许可证表达式。现在项目元数据声明 `GPL-3.0-or-later`，并使用支持 PEP 639 的 setuptools 要求。历史离线构建已验证 wheel `METADATA` 包含 `License-Expression`，wheel 与 sdist 都包含 `LICENSE`。

### 8. 学生核心资料仍有英文版本 — 已修复

API、架构、答辩速查、技术选型和第三方声明原先大段为英文，不利于独立理解和中文答辩。现已改为中文，并保留代码/API/许可证的原始术语。第三方声明补充了 WhatWeb、HTTPArchive/wappalyzer、wappalyzer-next 的核对 commit、仓库许可证、是否复用/修改及来源链接。

## Nice to have

### 9. 图表分块仍超过 Vite 500 kB 提示线（2026-11-05 复核为已修复）

原记录称图表"已经独立分块并按结果页需要加载"，该判断有误。复核生产产物 `frontend/dist/index.html` 发现首页带 `modulepreload` 指向 540.47 kB（gzip 189.29 kB）的图表分块，首屏就会预取，而首页 `DashboardView` 并不使用 echarts。它不是无害的体积提示，是真实的首屏缺陷。

根因在 `frontend/vite.config.ts` 的 `manualChunks`。它把 echarts、zrender 与 vue-echarts 强制归到 `charts` 分块，Rollup 随后把 Vue 运行时等共享依赖也吸进同一分块，导致 `DashboardView`、`ReportsView`、`SettingsView`、`CompareView`、`useScanHistory` 全部反向依赖它。`TechnologyChart` 本身已是 `defineAsyncComponent` 懒加载，手动分块反而破坏了按需加载。

修复只有一处，删除 `manualChunks` 整段，交由 Rollup 按动态 import 自然切分。修复后首页 `modulepreload` 数量为 0，首屏 gzip 从 260.59 kB 降到 102.86 kB，约减少 60.5%。echarts 落在 `TechnologyChart` 懒加载分块 458.82 kB（gzip 157.39 kB），@vue-flow 落在 `ArchitectureGraph` 懒加载分块 163.64 kB。最大分块低于 500 kB，Vite 体积提示消失。

验证：`./scripts/verify-all.sh` 退出码 0，后端 24 passed、前端 7 files / 8 tests、构建 2250 模块。运行中服务首页与 `dist/index.html` 字节一致，两个懒加载分块均可按 200 取回，核心 API 与报告导出正常。本轮没有做真实浏览器的图表渲染交互验收。

## 安全与数据路径审查结论

- 扫描器只执行普通 GET。`validate_target` 限定 HTTP(S)、拒绝 URL 凭据，并拒绝任意私网/本机/保留 DNS 地址；网络层连接已校验 IP。重定向逐跳重新校验，`trust_env=False`，并有限制超时、重定向次数和响应体大小。
- 完整 HTML 只在单次检测的内存对象里参与解析/匹配。SQLite 保存有限摘要、技术、证据和用户主动生成的 AI 报告。
- 每项技术都和具体命中证据关联；内部评分封顶 100，不称为概率。历史缺失项使用“本次未观察到”。
- AI Base URL 是独立的用户配置边界，可以是本机/私网；这个例外不会放宽扫描器。API Key 使用 `SecretStr` 接收，只留在进程内存，测试覆盖不返回、不写数据库以及完整回显时替换。
- HTML 报告对网页/AI/规则内容做转义。前端搜索未发现 `v-html`，不可信内容通过 Vue 文本插值显示。
- 服务绑定 `127.0.0.1` 且没有账号认证，适合本机单用户，不应暴露到共享网络。

## 本轮验收边界

- 没有对未授权外部网站发起新扫描；识别和安全行为由受控 fixture、mock DNS/重定向及现有历史记录验证。
- 没有调用真实 AI 提供方；AI 行为使用 mock/本地测试服务覆盖。
- 浏览器页面的 HTTP/SPA 深链可以做运行冒烟，但如果没有可用浏览器自动化控制，就不能把它写成已完成鼠标、键盘、视觉或无障碍验收。
- 没有把 `pnpm audit` 或第三方漏洞数据库扫描作为本轮要求，因此不能声称依赖不存在已知漏洞。
- 参考项目许可证核对只覆盖记录的具体 commit 与仓库级许可证；未来导入任何规则/数据仍需逐文件重新核对。

**Verdict:** 当前本机毕业设计主链路健康；本轮已复现的功能、中文体验、测试和元数据问题均已修复并重新验收。剩余的 540.47 kB 图表分块是性能提示，不阻塞当前交付。

**Not checked:** 真实 AI 提供方、未授权外部网站、鼠标/键盘视觉与无障碍自动化、浏览器实际打印 PDF、依赖漏洞数据库扫描，以及未来新增第三方指纹数据的逐文件授权条件。
