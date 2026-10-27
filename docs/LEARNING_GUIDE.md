# SiteLens AI 学习手册

这份手册用于帮助你读懂代码、解释取舍并亲自做小改动。阅读时先合上答案，用“自测”复述；不会的地方再回到代码。不要把置信等级说成概率，也不要把未观察到的信号说成技术已被移除。

## 1. 项目做什么

SiteLens AI 对用户声明有权检查的网站发起普通 HTTP GET，读取公开响应中的少量信号，再用 JSON 指纹规则识别技术。每项识别都带有来源、命中内容和规则权重。可选 AI 根据这些结构化结果生成解释，但不会决定某技术是否存在。

系统不做漏洞扫描、登录绕过、动态浏览器渲染或私网扫描；不保存完整网页。检测结果只说明这次公开响应观察到了什么。

## 2. 先认识目录

| 位置 | 作用 |
| --- | --- |
| `frontend/src/components/ScanForm.vue` | 输入 URL、取得用户授权声明并提交 |
| `frontend/src/api.ts` | 把页面操作转换成 `/api` HTTP 请求 |
| `frontend/src/views/ScanView.vue` | 读取并展示扫描结果、证据及 AI 报告 |
| `backend/app/main.py` | FastAPI 路由、流程编排、数据库读写及报告导出 |
| `backend/app/security.py` | URL/DNS 校验和已验证 IP 的网络传输 |
| `backend/app/fetcher.py` | GET、逐跳重定向处理、响应解析和信号整理 |
| `backend/app/detector.py` | 读取规则、匹配信号、累计分数和建立证据 |
| `backend/fingerprints/technologies.json` | 本项目编写的技术识别规则 |
| `backend/app/models.py` | SQLite 表结构 |
| `tests/backend/` | 安全、采集、规则、API、AI 和演示夹具测试 |

## 3. 一次扫描从哪里走到哪里

```text
ScanForm.vue
  └─ api.createScan(url)
       └─ POST /api/scans {url, authorized}
            └─ main.py:create_scan
                 ├─ 检查授权声明
                 ├─ fetcher.py:fetch_page
                 │    ├─ security.py:validate_target
                 │    ├─ PinnedTransport 发普通 GET
                 │    ├─ 每次重定向后重新校验目标
                 │    └─ parse_snapshot → PageSnapshot
                 ├─ detector.py:detect(page.signals())
                 ├─ 写入 scan / technology / evidence
                 └─ 返回扫描摘要
       └─ 跳转 /scans/{id}
            └─ ScanView.vue → GET /api/scans/{id}
```

### 前端如何提交

`ScanForm.vue` 保存 URL 和勾选状态；未勾选时不提交。`api.createScan` 把它转为 JSON 请求。后端的 `ScanRequest.authorized` 默认是 `false`，`create_scan` 再次拒绝没有授权声明的请求。

这里的授权是用户声明，不是所有权验证。网页勾选框无法证明用户拥有网站；答辩时应准确这样描述。

### 为什么先校验目标

`validate_target` 只接受 HTTP(S)，拒绝 URL 用户名密码、非法端口及解析到任意本机/私有/保留地址的主机名。如果 DNS 有多个答案，只要其中一个不属于公网地址就拒绝。这样可以降低扫描端点被拿来访问内网服务的风险。

校验之后，`PinnedBackend` 连接已校验的 IP，同时请求 URL 仍保留原主机名，供 HTTP Host 和 HTTPS TLS 校验使用。客户端禁用环境代理。重定向由程序手动处理；目标 URL 每跳重新走校验和 IP 固定。当前限制是总超时 10 秒、最多跟随 5 次重定向、最多读取 5 MiB 响应体。

AI Base URL 是不同的信任边界：只有用户主动配置的 AI 服务可以指向本机或私网；扫描器不会复用这个例外。

### PageSnapshot 里有什么

`parse_snapshot` 将 HTTP 响应整理为 `PageSnapshot`：原始/最终 URL、状态码、内容类型、标题、白名单响应头、白名单 Meta、脚本 URL、样式 URL，以及仅在内存中的 HTML 字符串。信号通过 `signals()` 交给规则引擎。

只提取样式表链接，不会进一步请求脚本或样式文件。URL 查询参数和片段会从持久化的目标及资源 URL 中去掉；响应头、标题和 Meta 值也有长度限制。

### 指纹如何变成技术与证据

规则文件的每项技术包含名称、分类和若干 `{source, pattern, weight}`。例如 Nginx 规则从 `header:server` 匹配 `nginx`；WordPress 可从 `meta_generator` 匹配名称，也可从 HTML 中匹配 `wp-content/`。

`detect` 根据规则来源取对应信号，使用不区分大小写的正则表达式匹配。每个匹配会生成一条 `Evidence`，包括来源、命中的文本、直接/间接类型和权重。相同来源和命中值不会重复计分；权重限制在 0–100，总分封顶 100。内部等级为：低于 40 是 low，40–69 是 medium，70 及以上是 high。这是项目内部规则分，不是统计概率，也没有经过真实站点样本校准。

直接证据目前指响应头和 generator Meta；脚本路径、样式路径及 HTML 特征归为间接信号。识别结果没有证据就不会被返回。

### 什么会保存到 SQLite

`ScanRow` 保存扫描时间、状态、标题、内容类型、净化后的 URL 和摘要 JSON；`TechnologyRow` 保存识别名称、分类、分数和等级；`EvidenceRow` 保存每条匹配证据；`AIReportRow` 保存用户生成的分析文本和模型名。表通过 ID/外键关联。

完整 HTML 不写入数据库。它只在这一次扫描的内存流程中参与匹配，之后随请求结束释放。这样可以减少不必要的网页数据留存；因此历史记录只包含已保存的摘要和证据。

## 4. 结果、历史、报告与 AI

### 结果页

`ScanView.vue` 按扫描 ID 加载结果。概览显示技术分类；Evidence 页把每项技术和来源/命中值对应起来。架构图把同一次响应中共同观察到的技术连线，因此只是关系假设，不代表网站真实内部部署拓扑。

### 历史比较

`compare_results` 比较两次已保存的识别名称及证据，分成新观察到、当前未观察到、证据变化和证据相同。差异可能来自页面变化、响应变化或规则覆盖范围；“本次未观察到”不证明技术已移除。

### HTML / JSON 报告

`/api/reports/{scan_id}/export?format=json` 导出该扫描结构化内容；`format=html` 生成可打印页面。HTML 对外部内容做转义。需要 PDF 时在浏览器中使用打印并保存为 PDF；项目没有独立 PDF 引擎。

### AI 分析

AI 配置存在 FastAPI 进程内存中，重启服务就清除。API Key 通过请求头发给用户配置的服务，不返回给前端、不写 SQLite；后端会从 AI 输出中替换完整回显的密钥。AI 响应大小受限且不自动跟随重定向。

结果页会展示发送前的结构化数据预览并要求确认，后端也检查确认字段。实际发送的是 URL、标题、状态、识别名称/分类/等级和证据，不包含完整 HTML。目标、标题和证据内容被明确视为不可信输入。AI 文本用 Vue 插值展示，不作为 HTML 执行。

## 5. 如何运行和验证

首次安装依赖并构建前端：

```sh
uv sync --all-extras
cd frontend
pnpm install --frozen-lockfile
pnpm build
cd ..
./scripts/start-local.sh
```

在 `http://127.0.0.1:8000` 打开应用。启动器只绑定本机回环地址。不要把没有认证的单用户服务暴露到共享网络。

常用检查：

```sh
.venv/bin/pytest -q
.venv/bin/ruff check backend tests
pnpm --dir frontend test
pnpm --dir frontend build
```

`test_demo_sites.py` 在测试中启动两个本地受控 HTML 页面，并替换测试用 DNS 校验以验证采集、服务器头和指纹匹配。这个替换只为测试使用；生产扫描仍然拒绝 loopback。它证明规则链路在可控样本上的行为，不代表对整个互联网技术识别覆盖率的统计结论。

## 6. 术语与答辩常见误区

| 术语 | 本项目中的意思 |
| --- | --- |
| 信号 | 响应头、Meta、HTML 或资源 URL 中可观察到的值 |
| 指纹规则 | 某种信号与模式之间的匹配条件及项目设定的权重 |
| 证据 | 某次规则命中的来源、文本、类型和权重 |
| 内部置信等级 | 按规则权重求和后的等级标签，不是概率 |
| 架构推测 | 对同一响应中共同出现技术的可视化假设 |
| 未观察到 | 当前响应中没有匹配到；不能推断其不存在或已移除 |
| 授权声明 | 用户确认有权分析；系统本身无法核实所有权 |

答辩不要说：系统能还原网站全部真实技术栈、high 等于某个百分比、AI 负责识别技术、比较结果证明技术被移除、项目已测试所有真实网站，或 AI 密钥会永久保存。

## 7. 分步自测

先自己说，再对照上文：

1. 从点击 Analyze 到结果页，函数/接口的顺序是什么？
2. 为什么只检查主机名不够？为什么要固定 IP，并在重定向后再检查？
3. `PageSnapshot.signals()` 传给了哪个函数？结果为什么同时包含技术和证据？
4. 权重怎样影响分数？为什么不能把分数解释成概率？
5. 哪些数据留在内存，哪些写入 SQLite？
6. 为什么 AI 可配置本机 URL，但网站扫描不能访问本机 URL？
7. 两个本地夹具测试证明了什么、没有证明什么？

能够指出代码位置并用自己的语言答出这些问题后，再尝试自行改一条有依据的指纹规则并补测试。改动必须从公开、合法采集的信号出发；不要为了让测试“通过”而凭空增加规则。
