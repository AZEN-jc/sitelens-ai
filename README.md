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

[学习手册](docs/LEARNING_GUIDE.md) · [答辩稿](docs/DEFENSE_SCRIPT.md) · [架构](docs/ARCHITECTURE.md) · [API](docs/API.md) · [验收记录](docs/TEST_REPORT.md) · [下一步](docs/NEXT_STEPS.md)

## 开源许可

本项目采用 GPL-3.0-or-later 许可证，详见 [LICENSE](LICENSE)。欢迎查看源码、复现实验结果或提交改进。
