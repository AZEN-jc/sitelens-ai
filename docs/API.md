# API 参考

所有接口都由本机 FastAPI 服务提供，统一位于 `/api` 下。创建检测是同步操作；错误会通过 `detail` 返回简短中文说明。API 不返回也不保存完整网页 HTML。

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `GET` | `/api/health` | 检查本机服务是否正常 |
| `POST` | `/api/scans` | 创建检测，请求体：`{ "url": "https://…", "authorized": true }` |
| `GET` | `/api/scans?limit=30&offset=0` | 分页读取检测摘要；不返回 AI 正文，`limit` 为 1–100，`offset` 从 0 开始 |
| `GET` | `/api/scans/count` | 返回已保存检测总数 |
| `GET` | `/api/scans/{scan_id}` | 返回一条检测、技术识别结果、证据和已保存 AI 报告 |
| `GET` | `/api/scans/{scan_id}/evidence` | 按技术返回证据 |
| `POST` | `/api/scans/compare` | 比较两次检测，请求体：`{ "first_scan_id": 1, "second_scan_id": 2 }` |
| `GET` | `/api/ai/config` | 查询 AI 是否已配置，以及非敏感的地址/模型信息 |
| `POST` | `/api/ai/config` | 在后端内存设置 `{ "base_url": "…", "api_key": "…", "model": "…" }` |
| `DELETE` | `/api/ai/config` | 清除后端内存中的 AI 配置 |
| `POST` | `/api/ai/test` | 测试当前 AI Chat Completions 连接 |
| `POST` | `/api/ai/analyze` | 分析指定检测，请求体：`{ "scan_id": 1, "confirm_data_sent": true }` |
| `GET` | `/api/reports` | 读取最近保存的 AI 分析报告 |
| `GET` | `/api/reports/{report_id}` | 读取一份 AI 报告及关联检测 |
| `GET` | `/api/reports/{scan_id}/export?format=html\|json` | 导出一条检测；HTML 带打印样式，可在浏览器中打印为 PDF |

## 答辩时要讲清的接口边界

- `POST /api/scans` 只有在 `authorized=true` 时才继续，表示用户声明自己拥有或获准分析目标。软件不能独立证明所有权。
- 扫描 URL 和 AI Base URL 使用两套不同的信任规则。扫描器拒绝本机、私网和保留地址；AI Base URL 是用户主动配置的服务，因此可以指向本机或私网。
- AI 分析前端必须先展示待发送的最小结构化数据，并由用户确认；API Key 不会通过状态接口返回。
- 历史比较里某项技术没有再次命中，只能解释为“本次未观察到”，不能据此断定目标已移除该技术。
