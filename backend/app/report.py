"""Render the self-contained HTML detection report.

The report mirrors everything the result page shows: verdict, site profile,
per-technology evidence, resource list and AI analysis, in the same visual
language as the product UI."""
from __future__ import annotations

import html
from typing import Any

CONFIDENCE_ZH = {"high": "高", "medium": "中", "low": "低"}
HEADER_LABELS = {
    "server": "服务器身份（Server）",
    "x-powered-by": "框架标识（X-Powered-By）",
    "via": "经过的代理（Via）",
    "cf-ray": "Cloudflare 节点编号（CF-Ray）",
    "content-type": "内容类型（Content-Type）",
}
META_LABELS = {
    "generator": "页面生成器声明",
    "application-name": "应用名称",
    "og:site_name": "站点名称",
    "robots": "搜索引擎抓取规则",
    "viewport": "移动端适配声明",
}

_CSS = """
body{font:14px/1.8 ui-monospace,SFMono-Regular,Menlo,Consolas,"PingFang SC","Microsoft YaHei",monospace;background:#0a0a0a;color:#eaeaea;max-width:920px;margin:0 auto;padding:44px 26px 60px}
h1{font-size:30px;font-weight:800;letter-spacing:-.05em;line-height:1.05;margin:0 0 6px}
h2{font-size:15px;font-weight:700;letter-spacing:-.02em;margin:0 0 4px}
h3{font-size:13px;font-weight:600;margin:0 0 10px;color:#9a9a9a}
.eyebrow{font-size:10px;letter-spacing:.12em;color:#8a8a8a;margin-bottom:10px}
.panel{border:1px solid #2a2a2a;background:#101010;padding:16px 18px;margin:14px 0}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1px;background:#2a2a2a;border:1px solid #2a2a2a;margin:14px 0}
.cell{background:#101010;padding:14px 16px}
.cell h3{margin-top:0}
dl{margin:0}
dt{color:#8a8a8a;font-size:11px;margin-top:9px}
dd{margin:2px 0 0;word-break:break-all}
dd code{color:#d0d0d0;font-size:12px}
.why{color:#8a8a8a;font-size:11px;line-height:1.7;margin:3px 0 0;max-width:52em}
.verdict{border-left:3px solid #e61919;padding:14px 16px;background:#141414;border-top:1px solid #2a2a2a;border-right:1px solid #2a2a2a;border-bottom:1px solid #2a2a2a;margin:14px 0}
.verdict.tentative{border-left-color:#8a8a8a}
.verdict .tag{font-size:10px;letter-spacing:.1em;color:#e61919;border:1px solid #e61919;padding:2px 8px;margin-right:10px}
.verdict.tentative .tag{color:#8a8a8a;border-color:#8a8a8a}
.verdict strong{font-size:15px}
.verdict p{color:#9a9a9a;font-size:12px;margin:8px 0 0}
.tech{border:1px solid #2a2a2a;background:#101010;padding:14px 16px;margin:10px 0}
.tech .meta-line{color:#8a8a8a;font-size:11px;margin:2px 0 8px}
.score{height:6px;background:#1c1c1c;margin:8px 0 10px;position:relative}
.score i{position:absolute;inset:0 auto 0 0;background:#e61919}
.ev{border-top:1px solid #222;padding:8px 0}
.ev .kind{font-size:10px;letter-spacing:.08em;margin-right:8px;padding:1px 6px;border:1px solid #4a4a4a;color:#b8b8b8}
.ev .kind.direct{border-color:#e61919;color:#e61919}
.ev code{color:#d0d0d0;font-size:11px;margin-right:8px}
.ev p{display:inline;margin:0;font-size:12px;color:#c8c8c8;word-break:break-all}
.ev small{color:#6a6a6a;font-size:10px;margin-left:8px}
ul.resources{margin:4px 0 12px;padding:0;list-style:none}
ul.resources li{font-size:11px;color:#c8c8c8;word-break:break-all;margin:3px 0}
.foot{color:#6a6a6a;font-size:11px;line-height:1.8;margin-top:22px;border-top:1px solid #222;padding-top:14px}
.summary-row{display:flex;flex-wrap:wrap;gap:1px;background:#2a2a2a;border:1px solid #2a2a2a;margin:14px 0}
.summary-row span{background:#101010;padding:10px 16px;font-size:12px;color:#d0d0d0}
.summary-row small{display:block;color:#8a8a8a;font-size:10px}
@media print{body{background:#fff;color:#111;padding:10mm}.panel,.cell,.tech{background:#fff;border-color:#bbb}.verdict{background:#fff}.why,.eyebrow,dt,h3,.verdict p{color:#444}.foot{color:#666}}
"""


def _esc(value: Any) -> str:
    return html.escape(str(value))


def _interpret_server(value: str) -> str:
    v = value.lower()
    if "bws" in v:
        return "BWS 是百度自家研发的服务器程序。说明这个网站的核心设施是自研的，不是市面通用方案。"
    if "tengine" in v:
        return "Tengine 是淘宝在 Nginx 基础上改造的版本，国内大型网站常用。"
    if "openresty" in v:
        return "OpenResty 是带编程能力的 Nginx 变种，国内大厂常用它做流量入口。"
    if "nginx" in v:
        return "Nginx 是全球使用最广泛的网页服务器之一，说明网站跑在成熟的通用设施上。"
    if "apache" in v and "coyote" not in v:
        return "Apache 是历史最悠久的网页服务器之一，常见于传统建站方案。"
    if "iis" in v:
        return "IIS 是微软家的服务器，说明网站大概率运行在 Windows 服务器上。"
    if "cloudflare" in v:
        return "这个网站把流量放在 Cloudflare 的防护与加速网络后面。"
    return "网站主动报出了服务器程序的名称。这类自我介绍写在协议响应里，可信度高。"


def _header_interpretation(key: str, value: str) -> str:
    if key == "server":
        return _interpret_server(value)
    if key == "x-powered-by":
        return "网站后端使用的语言或框架，同样是网站自己承认的。不少站点出于安全考虑会隐藏它。"
    if key == "via":
        return "说明这次响应经过了中间的代理或缓存层，你看到的可能是缓存的副本。"
    if key == "cf-ray":
        return "说明这个网站使用了 Cloudflare 的防护或加速服务。"
    if key == "content-type":
        return "告诉浏览器用什么格式解析这次响应，网页就是 text/html。"
    return "这项信息由网站在响应中主动提供。"


def _tech_section(item: dict[str, Any]) -> str:
    confidence = CONFIDENCE_ZH.get(item["confidence"], "未知")
    evidence = "".join(
        f'<div class="ev"><span class="kind {"direct" if ev["kind"] == "direct" else ""}">'
        f"{'白纸黑字' if ev['kind'] == 'direct' else '旁证推断'}</span>"
        f"<code>{_esc(ev['source'])}</code><p>{_esc(ev['matched'])}</p>"
        f"<small>权重 {ev['weight']}</small></div>"
        for ev in item["evidence"]
    )
    return (
        f'<div class="tech"><h2>{_esc(item["name"])}</h2>'
        f'<div class="meta-line">类别：{_esc(item["category_label"])} · {confidence}置信等级 · 评分 {item["score"]}/100</div>'
        f'<div class="score"><i style="width:{min(100, int(item["score"]))}%"></i></div>'
        f"{evidence}</div>"
    )


def render_html_report(data: dict[str, Any]) -> str:
    technologies = data.get("technologies", [])
    confirmed = [t for t in technologies if any(ev["kind"] == "direct" for ev in t["evidence"])]
    suspected = [t for t in technologies if not any(ev["kind"] == "direct" for ev in t["evidence"])]

    if not technologies:
        verdict = (
            '<div class="verdict tentative"><span class="tag">初步发现</span><strong>没有足够把握下结论</strong>'
            "<p>本次响应没有命中任何已知指纹。这不代表该网站没有使用相关技术——有些踪迹藏在接口响应里，一次普通访问看不到。</p></div>"
        )
    elif confirmed:
        suspected_note = (
            f"另外发现了 {'、'.join(t['name'] for t in suspected)} 的踪迹，但只是靠文件名之类的旁证推断，仅供参考。"
            if suspected else ""
        )
        verdict = (
            '<div class="verdict"><span class="tag">检测结论</span>'
            f"<strong>可以确认这个网站使用了：{'、'.join(t['name'] for t in confirmed)}</strong>"
            f"<p>判断依据：这些技术在网站的响应头或页面声明里白纸黑字写明了自己的身份，就像身份证一样，不是靠猜的。{_esc(suspected_note)}</p></div>"
        )
    else:
        verdict = (
            '<div class="verdict tentative"><span class="tag">初步发现</span><strong>没有足够把握下结论</strong>'
            f"<p>这次发现了 {'、'.join(t['name'] for t in suspected)} 的踪迹，但都只是文件名、页面关键字之类的旁证，可能误判，所以不下定论。</p></div>"
        )

    headers = data.get("headers", {})
    header_rows = "".join(
        f"<dt>{_esc(HEADER_LABELS.get(key, key))}</dt><dd><code>{_esc(value)}</code></dd>"
        f'<dd class="why">{_esc(_header_interpretation(key, value))}</dd>'
        for key, value in headers.items()
    ) or '<dd class="why">网站没有自报服务器身份。很多站点出于安全考虑会隐藏这一项，所以没显示不等于没有服务器。</dd>'
    meta_rows = "".join(
        f"<dt>{_esc(META_LABELS.get(item['name'], item['name']))}</dt><dd>{_esc(item['content'])}</dd>"
        for item in data.get("meta", [])
    )
    scripts = "".join(f"<li><code>{_esc(item)}</code></li>" for item in data.get("scripts", [])[:15])
    styles = "".join(f"<li><code>{_esc(item)}</code></li>" for item in data.get("styles", [])[:15])
    ai = "".join(
        f'<div class="panel"><h2>AI 分析 · {_esc(item["model"])}</h2><pre style="white-space:pre-wrap;font-size:12px">{_esc(item["content"])}</pre></div>'
        for item in data.get("ai_reports", [])
    )
    duration = data.get("duration_ms") or 0
    page_bytes = data.get("page_bytes") or 0
    summary = f'<span><small>检测网址</small>{_esc(data["url"])}</span><span><small>最终地址</small>{_esc(data["final_url"])}</span><span><small>HTTP 状态</small>{data["status_code"]}</span>'
    if duration:
        summary += f"<span><small>响应耗时</small>{duration / 1000:.2f} 秒</span>"
    if page_bytes:
        summary += f"<span><small>页面大小</small>{page_bytes / 1024:.1f} KB</span>"
    tech_sections = "".join(_tech_section(item) for item in technologies) or '<div class="panel">没有匹配到证据。</div>'
    return (
        "<!doctype html><html lang='zh-CN'><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>网站检测报告</title><style>" + _CSS + "</style>"
        '<div class="eyebrow">SITELENS · 检测报告</div>'
        "<h1>网站检测报告</h1>"
        f'<div class="summary-row">{summary}</div>'
        f"<div class='panel'><h2>{_esc(data['title'])}</h2><p style='margin:0;color:#9a9a9a;font-size:12px'>检测时间 {_esc(data['created_at'].isoformat())} · 内容类型 {_esc(data.get('content_type') or '未知')}</p></div>"
        + verdict
        + f'<div class="grid2"><div class="cell"><h3>响应头明细</h3><dl>{header_rows}</dl></div>'
        + (f'<div class="cell"><h3>页面声明</h3><dl>{meta_rows}</dl></div>' if meta_rows else "")
        + "</div>"
        + f'<div class="panel"><h3>技术识别结果</h3>{tech_sections}</div>'
        + (f'<div class="panel"><h3>外部资源清单</h3><ul class="resources">{scripts}{styles}</ul></div>' if (scripts or styles) else "")
        + ai
        + '<div class="foot">识别依据为公开响应证据。标注「白纸黑字」的结论来自响应头或页面声明的直接证据，可以打开对应网址查看源码核实；'
        "标注「旁证推断」的仅依赖脚本命名、页面关键字等间接特征。置信等级是项目内部规则分数，不代表统计概率。"
        "本次缺少证据不代表技术已被移除。本报告由本机工具生成，检测过程只发起了一次普通网页访问。</div></html>"
    )
