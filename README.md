# SiteLens AI

**基于 Python 与人工智能的网站技术特征识别与分析系统**，用于对你拥有或获准检测的网站进行本机分析。每项技术识别都会列出对应的公开证据；AI 只解释识别结果，不负责决定技术是否存在。

## 功能

- 通过普通 HTTP(S) GET 请求采集网站公开信号，并用 JSON 指纹规则识别技术。
- 查看每项识别结果的匹配证据、内部置信等级和技术分类。
- 在本机 SQLite 中保存检测历史，比较两次检测并导出 HTML、JSON 报告。
- 可选连接 OpenAI 兼容服务，对结构化检测摘要进行 AI 解读。
- 中文界面；本机单用户运行，不含账号系统或云端服务。

## 环境要求

- Python 3.11 或更新版本
- Node.js 22.22.2 或更新的 22.x，或 24.15.0 或更新版本
- pnpm 11

## 本机运行

首次安装依赖，之后每次启动只需一条命令：

```sh
uv sync --all-extras
cd frontend && pnpm install --frozen-lockfile && cd ..
./scripts/start.sh
```

`start.sh` 会自动构建前端、写入两条离线演示检测、启动服务并打开浏览器。打开 [http://127.0.0.1:8000](http://127.0.0.1:8000) 就能看到技术图表、匹配证据、历史比较和报告导出，不需要访问外部网站。服务只绑定本机回环地址，历史保存在 `data/sitelens.sqlite`。

如果没有安装 uv，可使用 `.venv/bin/pip install -e '.[dev]'` 安装后端依赖；`uv.lock` 记录 Python 依赖版本。

前端开发时，先在一个终端启动 API：

```sh
.venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

再在另一个终端启动 Vite：

```sh
cd frontend
pnpm dev
```

## 使用流程

1. 输入 HTTP(S) 地址，并确认你拥有该网站或已获得检测许可。
2. 查看识别结果及每项技术对应的响应证据。
3. 如需 AI 解读，在“设置”中配置兼容 OpenAI Chat Completions 的服务。API 密钥只保存在后端内存中，服务重启后清除。
4. 生成 AI 分析前，先查看将发送的结构化摘要并确认发送。
5. 可比较历史检测，或导出 HTML、JSON；HTML 报告可通过浏览器“打印”另存为 PDF。

## 安全边界与局限

扫描器只发起普通公开 HTTP GET 请求，会拒绝本机、私有和保留地址；每次重定向都会重新校验目标，并连接到已校验的 DNS 地址。请求超时为 10 秒，最多跟随 5 次重定向，最多读取 5 MiB。系统不进行漏洞探测或访问控制绕过。授权勾选是用户声明，软件不能独立验证网站所有权。

配置本机或私有网络 AI 地址属于单独的信任决定，不会放宽扫描器的目标限制。系统不含用户认证，请勿将服务暴露到共享网络。动态浏览器渲染识别也不属于当前版本能力。

## 验收与学习材料

- [中文学习手册：代码地图、扫描链路、安全边界与自测题](docs/LEARNING_GUIDE.md)
- [5–8 分钟答辩稿、现场演示与常见问题](docs/DEFENSE_SCRIPT.md)
- [AI 辅助使用记录](docs/AI_USAGE_LOG.md)
- [验收记录](docs/TEST_REPORT.md)
- [完整审查记录与后续改进项](docs/AUDIT_REPORT.md)
- [架构与 API 文档](docs/ARCHITECTURE.md) · [API 参考](docs/API.md)
- [技术选型记录](docs/TECH_SELECTION.md) · [第三方声明](THIRD_PARTY_NOTICES.md)

## 检查

在项目根运行一键脚本，依次执行后端测试、Ruff、前端测试与前端构建，任一步失败立即停止：

```sh
./scripts/verify-all.sh
```

也可以分步手动执行：

```sh
.venv/bin/pytest
.venv/bin/ruff check backend tests
cd frontend && pnpm test && pnpm build
```

部分 IDE 会向终端注入 `NODE_OPTIONS` 与 `PYTHONPATH`。前者通过 `--require` 把语言服务 shim 挂到每个 Node 进程，vitest 的 forks worker 继承后初始化握手会卡住，60 秒后超时，表现为前端测试全部报错。后者指向宿主文件代理，pytest 的临时目录在已存在时会报 `EEXIST`。`verify-all.sh` 在开头清除这两个变量，让测试回到干净的进程环境。手动分步执行时若遇到前端超时，可改用 `env -u NODE_OPTIONS pnpm test`；后端临时目录报错可改用 `env -u PYTHONPATH ./.venv/bin/pytest -q`。这些属于宿主环境干扰，不是项目源码问题，不要为此修改 vite 配置或测试。
