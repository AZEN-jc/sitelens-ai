---
task_id: "sitelens-handoff-01"
role: "implementer"
target_agent: "codex"
playbook: ".agents/pstack/playbooks/bug-fix.md"
required_principles:
  - ".agents/pstack/principles/prove-it-works.md"
  - ".agents/pstack/principles/no-comments.md"
  - ".agents/pstack/principles/unslop-zh-en.md"
verify_cmd: "./scripts/verify-all.sh && pstack verify all"
---

## 1. User Goal (Restated)

把毕业设计 SiteLens AI 交接成任何机器上都能一键复现验收的状态。本轮不新增产品功能，不修改后端业务代码，只补齐可复现的验收入口与真实记录。用户明确要求先规划再执行，主控已完成复现与根因剥离。

## 2. Consolidated Directives (History & Delta)

- [Init] 已在项目根初始化 pstack 轻量工作区，项目自带 `AGENTS.md` 未被覆盖。
- [Round 1 已否决] 不要修改 `frontend/vite.config.ts` 的 pool 配置。实测证明默认 forks pool 在干净环境下 4.28s 全绿，改配置是修症状。
- [Round 1 已否决] 不要给 `ReportsView.vue` 或 `ReportsView.test.ts` 打补丁。该报错只在 vmThreads 下出现，是测试运行器上下文假象。
- [Delta] 保留工作树现有的 `ScanView.vue` 与 `ScanView.test.ts` 改动，不要 reset、不要 commit、不要改内容。
- [Delta] 只交付三处文件改动：新增一键验收脚本、README 检查段、验收记录追加本轮实测。文档数字必须来自本轮真实运行，禁止沿用旧数字或写"应该通过"。
- [Delta] 中文文档禁用破折号、AI 腔套话和空泛结论；脚本注释不得复述代码行为。

## 3. Evidence Pointers (Read-Only Context)

- 复现与根因全表：`.agents/handoffs/evidence-pack.md:1-60`
- 产品定义与运行要求：`README.md:1-8`
- 项目安全与工程约束：`AGENTS.md:1-8`
- 上轮审查结论：`docs/AUDIT_REPORT.md:1-88`
- 上轮验收声明与文档体例：`docs/TEST_REPORT.md:1-101`
- 现有启动脚本体例：`scripts/start-local.sh:1-12`
- 前端测试配置：`frontend/vite.config.ts:1-20`
- 已验证通过的遗留改动：`frontend/src/views/ScanView.vue:16-40`
- 已验证通过的遗留测试：`frontend/tests/ScanView.test.ts:22-62`
- 剧本与铁律：`.agents/pstack/playbooks/bug-fix.md:1-30`、`.agents/pstack/principles/prove-it-works.md:1-40`
- 决策账本：`.agents/decision.tsv:1-1`

## 4. Deliverable Contract

1. 新增 `scripts/verify-all.sh`（可执行）：在项目根依次运行后端 pytest、Ruff、前端 test、前端 build；脚本内对测试命令清除继承的 `NODE_OPTIONS`，其余保持不变；缺依赖时给中文提示并非零退出；任一步失败立即停止。用真实命令跑通，报告实际退出码。
2. 更新 `README.md` 的「检查」段：给出一键脚本用法，并用一小段说明部分 IDE 会注入 `NODE_OPTIONS` 导致 vitest worker 超时的现象与规避方式。
3. 在 `docs/TEST_REPORT.md` 末尾追加一节 2026-11-04 记录：按证据包第 1 至 8 项列出真实命令与输出，写清根因归属宿主注入、项目源码未改、遗留改动已验证通过，并列出本轮未执行项。
4. 交付前自行运行 `./scripts/verify-all.sh`，贴出真实输出；主控会独立复跑并加跑端到端服务冒烟与 pstack 全量门禁。
5. 禁止修改任何后端文件、前端源码、vite 配置与现有测试；禁止 git commit、push 或任何网络发布动作。
