# SiteLens AI

基于公开证据的网站技术特征识别与分析系统。
每项识别都附带命中的响应证据；AI 只解释结果，不判断技术是否存在。

本机单用户运行，不依赖云端，不需要账号。

---

## 运行

首次安装依赖：

```sh
uv sync --all-extras
cd frontend && pnpm install --frozen-lockfile && cd ..
```

之后每次启动：

```sh
./scripts/start.sh
```

这一条会构建前端、写入两条离线演示检测、启动服务并打开浏览器。访问 [http://127.0.0.1:8000](http://127.0.0.1:8000) 就能看到技术图表、匹配证据、历史比较和报告导出，全程不需要外部网络。

环境：Python 3.11+、Node 22.22.2+ 或 24.15.0+、pnpm 11。

## 能力

- **01**　普通 HTTP GET 采集公开信号，JSON 指纹规则识别技术
- **02**　每项结果列出匹配证据、置信等级与技术分类
- **03**　本机 SQLite 保存历史，支持两次检测比较
- **04**　导出 HTML / JSON 报告，可打印为 PDF
- **05**　可选接入 OpenAI 兼容服务，对结构化摘要生成解读

## 边界

扫描器只做公开 GET，拒绝本机与私网地址，不探测漏洞、不绕过访问控制。
AI 密钥只留在后端内存，不写盘、不回传。服务只绑定 127.0.0.1，没有账号系统。
动态渲染识别、漏洞扫描、多用户部署都不在当前版本范围内。

## 检查

```sh
./scripts/verify-all.sh
```

## 文档

[演示动线](docs/DEMO_SCRIPT.md) · [技术总结](docs/TECHNICAL_SUMMARY.md) · [出镜分镜表](docs/DEFENSE_VIDEO_SCRIPT.md) · [系统图纸](docs/DIAGRAMS.md) · [学习手册](docs/LEARNING_GUIDE.md) · [答辩稿](docs/DEFENSE_SCRIPT.md) · [架构](docs/ARCHITECTURE.md) · [API](docs/API.md) · [验收记录](docs/TEST_REPORT.md)

## 开源许可

本项目采用 GPL-3.0-or-later 许可证，详见 [LICENSE](LICENSE)。欢迎查看源码、复现实验结果或提交改进。

## 提交前填写个人信息

毕业设计材料需要本人标识。把 `backend/app/report.py` 顶部四项常量替换为真实信息，导出的报告页脚就会带上。

离线演示包里有一份报告渲染副本，改完执行下面这条命令同步，否则答辩现场导出的报告仍是占位符。

```sh
cp backend/app/report.py demo/report.py
```

`docs/TECHNICAL_SUMMARY.md` 封面与 `docs/DEFENSE_VIDEO_SCRIPT.md` 台词里的占位符也要同步替换。产品界面本身不加姓名横幅。

## 答辩现场离线演示（零依赖）

机房电脑如果没有 Node.js、pnpm 或 uv，或者现场断网，用这条命令。

```sh
python3 scripts/serve-offline.py
```

只需要 Python 3 标准库。打开 `http://127.0.0.1:8010` 即可看到完整界面、12 条真实演示记录、结论与证据、历史对比和报告导出。离线包不发起任何外部请求，也不保存新检测。现场要做实时检测时用完整环境的 `./scripts/start.sh`。

离线包放在 `demo/`。`site.zip` 是前端构建产物，`scans.json` 是演示数据快照，`report.py` 是报告渲染副本。改过前端或报告后重新执行 `pnpm build`，再重新生成 `demo/site.zip` 与 `demo/report.py`。
