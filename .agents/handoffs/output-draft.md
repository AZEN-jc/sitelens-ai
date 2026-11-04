# Pstack Output Draft

SiteLens AI 交接与首屏修复结论 [实测 Measured]

后端 24 项测试与 Ruff 静态检查全绿。前端 7 个测试文件共 8 项测试在清除宿主注入后全部通过。

两处验收失败都来自宿主注入。NODE_OPTIONS 卡住 vitest worker，PYTHONPATH 破坏 pytest 临时目录。项目源码没有因此改动。

复核发现首页会预加载 540.47 kB 的图表分块。删除 vite 配置里的手动分块规则后，首屏 gzip 从 260.59 kB 降到 102.86 kB。图表改为真正按需加载，Vite 体积提示消失。

本轮交付一键验收脚本，并把复现实验、端到端冒烟与修复前后数据写入验收记录。本机服务冒烟全绿。
