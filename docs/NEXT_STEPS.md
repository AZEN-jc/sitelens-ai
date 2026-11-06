# 下一步规划：收敛成开箱即用的小工具

## 判断

工程验证已经够了。缺的不是功能，是第一次打开时能演示的内容 [实测 Measured]。

- `data/sitelens.sqlite` 现有 1 条检测记录，技术 0 条、证据 0 条、AI 报告 0 条。
- 首页、结果图表、证据页、历史比较和报告导出在全新安装后都是空的。
- 启动需要 5 步，还要手动构建前端并手动打开浏览器。
- 文档共 861 行，`TEST_REPORT.md` 269 行，README 87 行且含环境排障内容。

## 原则

功能不再增加。只做让已有能力一打开就看得见的事。工程过程产物不进入交付主路径。

## U1 内置演示数据（已完成）

用仓库已有的 `demo-sites/wordpress/index.html` 与 `demo-sites/react/index.html`，经项目 `detector` 生成两条带技术和证据的记录写入 SQLite。不发起外部请求，不改安全边界，脚本幂等。

- 验证命令 `./scripts/verify-all.sh` 全绿。
- `GET /api/scans/count` 返回 3，`GET /api/scans/2` 的技术列表非空。
- 浏览器打开结果页能看到图表与证据。

## U2 一键启动（已完成）

把 5 步压成一条 `./scripts/start.sh`。检测依赖，缺前端产物时自动构建，起服务后打开浏览器，失败给中文提示。

- 验证命令是删掉 `frontend/dist` 后运行 `./scripts/start.sh`。
- 首页返回 200，浏览器被唤起。

## U3 交付面减法（已完成）

README 顶部换成 30 秒快速开始，环境排障与验证材料清单移到 docs。`.agents/` 加入 `.gitignore`。`TEST_REPORT.md` 保留为验收证据，不再从 README 正文反复链接。

- 验证命令 `pstack verify all` 全绿。
- README 首屏只剩运行方式和一句产品说明。

## 明确不做

- 不加账号、云端、动态渲染、更多指纹规则或新页面。
- 不新增验收脚本、审查报告或工作流文件。
- 不升级依赖。漏洞比对发现的 4 处公告都在开发期工具，不影响本机演示。
- 不为外部扫描放宽 `trust_env=False` 或启用环境代理。
- 不动已验过的安全边界与业务源码。

## 实测结果

- `scripts/seed-demo.py` 复用 `parse_snapshot` 与 `detect`，离线生成 2 条记录、4 项技术、6 条证据。二次运行跳过，幂等成立。
- `summary_json` 只存 headers、meta、scripts、styles，不含页面 HTML。
- `scripts/start.sh` 一条命令起服务，`/api/scans/count` 返回 3，两条演示记录的技术与证据都可读。
- 两种格式的报告导出共 4 次全部 200，历史比较正确返回新增项与未观察项。
- Chrome 156 用真实数据渲染出 canvas 309×183、2 张技术卡片、架构图 3 节点，图表分块仍是懒加载。
- `./scripts/verify-all.sh` 与 `pstack verify all` 全绿。
- U3 把 README 从 87 行压到 46 行，首屏只剩定位、运行、能力、边界、检查与一行文档链接。环境排障长段移出，完整记录仍在 `TEST_REPORT.md`。
- Chrome 156 实测主题切换从 dark 到 light 正常，编号列表 4 行完整，没有重叠或截断。
- `.agents/` 加入 `.gitignore` 并从版本库移除 4 个过程文件，本地与 git 历史都保留。
- 三个单元全部完成。`./scripts/verify-all.sh` 与 `pstack verify all` 仍全绿。
