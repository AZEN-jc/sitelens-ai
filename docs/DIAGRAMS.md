# 系统图纸（校正版备用） [实测 Measured]

> 图纸属于实物设计与制作类的必交材料。本次任务书选的是实践操作类，本文件仅作备用。
> 全部图按当前仓库真实模块绘制。原方案图纸里的「个人标识横幅」并不存在于界面，已删去。

图纸使用 Mermaid 语法。可粘贴到 Typora、VS Code 的 Mermaid 插件或 mermaid.live 导出 PNG。

## 图纸 1 系统总体架构图

```mermaid
graph TB
    subgraph 表现层_Vue3单页应用
        A1[扫描输入 ScanForm]
        A2[概览首页 DashboardView]
        A3[检测结果 ScanView]
        A4[历史对比 CompareView]
        A5[报告与设置视图]
    end
    subgraph 接口层_FastAPI
        B1[扫描端点 /api/scans]
        B2[历史与对比端点]
        B3[报告导出端点]
        B4[AI 配置与分析端点]
    end
    subgraph 业务层
        C1[security.py 域名与IP校验]
        C2[fetcher.py 公开信号采集]
        C3[detector.py 规则匹配计分]
        C4[report.py 报告渲染]
        C5[ai_service.py 可选解读]
    end
    subgraph 数据层
        D1[(SQLite 检测记录)]
        D2[(SQLite 技术与证据)]
        D3[technologies.json 61条规则]
    end
    A1 --> B1
    A2 --> B2
    A3 --> B3
    A5 --> B4
    B1 --> C1 --> C2 --> C3
    C3 --> D1
    C3 --> D2
    D3 --> C3
    B3 --> C4
    B4 --> C5
    D1 --> B2
    D2 --> B3
```

## 图纸 2 检测与安全校验工作流程图

```mermaid
flowchart TD
    S[输入网址] --> P[无协议头时自动补 https]
    P --> V{DNS 解析与 IP 校验}
    V -->|私网或保留地址| R1[拒绝并返回中文提示]
    V -->|公网地址| G[发送一次公开 GET]
    G --> J{是否跳转}
    J -->|是且未超过5次| V
    J -->|否| L[检查体积上限与超时]
    L --> E[提取响应头 页面声明 脚本 样式 标题]
    E --> M[61条规则逐条正则匹配计分]
    M --> C{有无直接证据}
    C -->|有| K1[结论面板标为可以确认]
    C -->|无| K2[结论面板标为仅供参考]
    K1 --> W[写入 SQLite 并展示]
    K2 --> W
    W --> X[导出 HTML 或 JSON 报告]
```

采集器禁用环境代理，响应体上限 5 MiB，超时 30 秒。跳转时每一跳都重新校验 IP。

## 图纸 3 数据库实体关系图

```mermaid
erDiagram
    ScanRow ||--o{ TechnologyRow : 包含
    TechnologyRow ||--o{ EvidenceRow : 附带
    ScanRow ||--o{ AIReportRow : 可选分析
    ScanRow {
        int id PK
        string url
        string final_url
        int status_code
        string title
        string summary_json
        datetime created_at
    }
    TechnologyRow {
        int id PK
        int scan_id FK
        string name
        string category
        int score
        string confidence
    }
    EvidenceRow {
        int id PK
        int technology_id FK
        string source
        string matched
        string kind
        int weight
    }
    AIReportRow {
        int id PK
        int scan_id FK
        string model
        string content
        datetime created_at
    }
```

`summary_json` 保存响应头、页面声明、脚本、样式、耗时与页面大小。页面 HTML 正文不落库。

## 图纸 4 功能模块结构图

```mermaid
graph LR
    ROOT[SiteLens AI] --> F1[检测模块]
    ROOT --> F2[证据模块]
    ROOT --> F3[展示模块]
    ROOT --> F4[交付模块]
    F1 --> F11[裸域名输入]
    F1 --> F12[安全校验]
    F1 --> F13[公开采集]
    F1 --> F14[规则匹配]
    F2 --> F21[白纸黑字直证]
    F2 --> F22[旁证推断]
    F2 --> F23[信号人话解读]
    F3 --> F31[检测结论]
    F3 --> F32[网站档案带]
    F3 --> F33[资源清单]
    F3 --> F34[分类统计图表]
    F4 --> F41[HTML 报告]
    F4 --> F42[JSON 报告]
    F4 --> F43[一键启动与离线演示]
```

## 图的核对依据 [实测 Measured]

模块名与端点名取自 `backend/app` 与 `frontend/src`。规则数 61 条取自 `technologies.json`。安全参数取自 `security.py`。数据实体取自 `models.py`。界面模块取自 `ScanView.vue` 与 `DashboardView.vue`。

图纸属于备用材料。实践操作类提交时以 `TECHNICAL_SUMMARY.md` 与 `DEFENSE_VIDEO_SCRIPT.md` 为准。
