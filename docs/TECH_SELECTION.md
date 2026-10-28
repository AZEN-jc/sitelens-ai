# Phase 0：技术与许可证选型记录

参考项目状态通过公开 GitHub 信息在 2026-10-25 做过一次时间点核对。维护活跃度只能说明当时状态，不保证未来继续维护。

| 参考项目 | 主要语言 | 仓库许可证 | 核对版本/状态 | SiteLens AI 的处理 |
| --- | --- | --- | --- | --- |
| [WhatWeb](https://github.com/urbanadventurer/WhatWeb) | Ruby | GPL-2.0 only；README 与许可证文本没有 “or later” | commit `d279d93042d034f3fd29d5a893d44ccc0595d3f8`；当时未归档，`pushed_at` 为 2026-04-02 | 只参考“插件/规则识别公开技术特征”的思路；未复制代码、插件或指纹数据 |
| [HTTPArchive/wappalyzer](https://github.com/HTTPArchive/wappalyzer) | JavaScript | GPL-3.0 | commit `bce5091d0ed2614a29c792436de1ac9080c3f51d`；当时未归档，`pushed_at` 为 2026-10-20 | 只参考技术数据树与检测器组织思路；未复制源码或数据 |
| [wappalyzer-next](https://github.com/s0md3v/wappalyzer-next) | Python | GPL-3.0 | commit `ff85c8b50485868a998f79f22e59d3cf1fe2f070`；当时未归档，`pushed_at` 为 2026-09-30 | 只参考 Python/浏览器识别方向；未复制源码或指纹数据 |

仓库级许可证不能自动代表其中每个规则、图标、fixture 或数据文件都采用相同授权。本项目没有导入这些上游规则，因此没有把任何上游指纹数据加入发行版。未来如果要复用某个具体文件，必须重新核对那个文件的来源提交、单独授权条款及与 GPL-3.0-or-later 的兼容性。尤其不能把 GPL-2.0-only 的 WhatWeb 代码直接合并进 GPL-3.0 组件。

## 最终技术方案

- **前端**：Vue 3 + TypeScript + Vite；Element Plus 提供表单与基础控件，Tailwind CSS 负责布局，ECharts 展示分类统计，Vue Flow 展示明确标注为推测的技术关系。
- **后端**：FastAPI 提供 `/api`，HTTPX/httpcore 执行受限 HTTP 采集，BeautifulSoup 提取公开响应中的有限信号。
- **识别规则**：项目自建 JSON 指纹目录，规则按来源匹配，并把命中证据保留下来。置信分数只是内部权重，不解释成概率。
- **本地存储**：SQLite + SQLModel。首版启动时通过 `create_all` 初始化固定 schema，不额外引入迁移框架。
- **AI**：用户配置 OpenAI 兼容 Chat Completions 地址、密钥和模型；密钥只留在后端内存。AI 解释识别结果，不参与规则判定。
- **报告**：后端生成 HTML 与 JSON。PDF 使用 HTML 打印样式和浏览器“打印为 PDF”，首版不增加服务端 PDF 引擎。

## 首版明确不做的内容

首版目标是“本机可演示、证据可追溯、历史可比较、答辩能解释”。因此 Playwright 动态浏览器扫描、后台任务队列、账号系统、云端部署、服务端 PDF 生成和统计概率校准都不属于当前核心验收范围。
