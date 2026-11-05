---
task_id: "sitelens-acceptance-02"
role: "verifier"
target_agent: "codex"
playbook: ".agents/pstack/playbooks/figure-it-out.md"
required_principles:
  - ".agents/pstack/principles/prove-it-works.md"
  - ".agents/pstack/principles/attack-the-premise.md"
verify_cmd: "pstack verify all"
---

## 1. User Goal (Restated)

补齐毕业设计此前明确列为未执行的四项验收：真实浏览器图表渲染交互、真实 AI 服务、外部网站扫描、依赖漏洞数据库扫描。产出可复验命令、真实命令输出与边界说明，供答辩使用。

## 2. Consolidated Directives (History & Delta)

- [Step 1] 立三条互斥假说并按实测剪枝。H1 四项都能自动补齐已证伪，H2 四项都做不到已证伪，采用 H3 分项判定。
- [Step 2 skip] 原生子 Agent 在上一轮两次实测 502 TLS 握手失败，修复 Clash GLOBAL 后仍失败。本轮改由主控用并行只读命令取证，全部证据写入证据包，不把 502 重试当进展。
- [Step 3] 不得为跑通验收放宽 `AGENTS.md` 的任何安全约束。扫描器禁用环境代理、AI 密钥只存内存、不持久化页面 HTML 三条保持原样。
- [Step 3] 外部扫描只对用户授权本轮演示的 IANA 保留示例域名发起普通 GET，不碰其他公网目标，不做漏洞探测。
- [Step 3] 真实模型提供方本机不存在，不得用测试替身冒充真实 AI。替身只用于验证配置、连接、密钥与确认门禁边界，文档中显式标注。
- [Step 4] 浏览器验收用 CDP Fetch 拦截返回受控 fixture，不写数据库、不改业务源码；脚本固化到项目供随时复跑。
- [Step 5] 所有结论按证据分级入账，交付前跑全量门禁。

## 3. Evidence Pointers (Read-Only Context)

- 安全边界：`AGENTS.md:1-10`
- AI 请求实现与禁用代理点：`backend/app/ai_service.py:26-48`
- 图表容器与架构图模板：`frontend/src/views/ScanView.vue:88-120`
- 既有验收记录体例：`docs/TEST_REPORT.md:1-10`
- 固化的浏览器验收脚本：`scripts/verify-browser.cjs:1-30`
- 本轮取证全表：`.agents/handoffs/evidence-pack.md:1-30`
- 剧本与铁律：`.agents/pstack/playbooks/figure-it-out.md:1-20`、`.agents/pstack/principles/prove-it-works.md:1-20`
- 决策账本：`.agents/decision.tsv:1-1`

## 4. Deliverable Contract

1. 四项各自给出真实命令、真实输出与明确判定，完成或阻塞都要写清，禁止把测试替身写成真实模型推理。
2. 新增可复验脚本并在验收记录里给出一键复跑命令与最小心智模型。
3. 依赖漏洞结果如实记录数量与公告 ID，不擅自升级依赖，不声称依赖零漏洞。
4. 更新证据包、交付摘要与决策账本，交付前 `pstack verify all` 必须全绿。
5. 不改后端业务代码、前端组件与接口，不 git push 到未授权的远端。
