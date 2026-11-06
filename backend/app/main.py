from __future__ import annotations

import html
import json
import os
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlmodel import Session, select

from app.ai_service import generate_ai_analysis, test_ai_connection, validate_ai_base_url
from app.database import initialize_database, make_engine
from app.detector import detect
from app.fetcher import fetch_page
from app.models import AIReportRow, EvidenceRow, ScanRow, TechnologyRow
from app.schemas import (
    AIAnalysisRequest,
    AIConfigIn,
    AIConfigView,
    CompareRequest,
    ScanOut,
    ScanRequest,
)
from app.security import TargetError

DEFAULT_DATABASE = Path(__file__).parents[2] / "data" / "sitelens.sqlite"
CATEGORY_NAMES_ZH = {
    "Analytics": "分析统计",
    "CDN": "内容分发网络",
    "CMS": "内容管理系统",
    "Frontend framework": "前端框架",
    "JavaScript library": "JavaScript 库",
    "Static site tool": "静态站点工具",
    "UI framework": "UI 框架",
    "Web framework": "Web 框架",
    "Web server": "Web 服务器",
}


def _technology_dict(session: Session, technology: TechnologyRow) -> dict:
    evidence = session.exec(select(EvidenceRow).where(EvidenceRow.technology_id == technology.id)).all()
    return {
        "name": technology.name,
        "category": technology.category,
        "category_label": CATEGORY_NAMES_ZH.get(technology.category, technology.category),
        "score": technology.score,
        "confidence": technology.confidence,
        "evidence": [
            {"source": item.source, "matched": item.matched, "kind": item.kind, "weight": item.weight}
            for item in evidence
        ],
    }


def _scan_dict(session: Session, scan: ScanRow, include_reports: bool = True) -> dict:
    summary = json.loads(scan.summary_json)
    technologies = session.exec(select(TechnologyRow).where(TechnologyRow.scan_id == scan.id)).all()
    reports = session.exec(
        select(AIReportRow).where(AIReportRow.scan_id == scan.id).order_by(AIReportRow.created_at)
        if include_reports else select(AIReportRow.id).where(AIReportRow.scan_id == scan.id)
    ).all()
    return {
        "id": scan.id,
        "url": scan.url,
        "final_url": scan.final_url,
        "status_code": scan.status_code,
        "content_type": scan.content_type,
        "title": scan.title,
        **summary,
        "created_at": scan.created_at,
        "technologies": [_technology_dict(session, item) for item in technologies],
        "ai_report_count": len(reports),
        "ai_reports": [
            {"id": item.id, "model": item.model, "content": item.content, "created_at": item.created_at}
            for item in reports
        ] if include_reports else [],
    }


def _private_url_parts_removed(value: str) -> str:
    return str(httpx.URL(value).copy_with(query=None, fragment=None))


def create_app(database_url: str | None = None) -> FastAPI:
    app = FastAPI(title="SiteLens AI", version="0.1.0")
    url = database_url or os.getenv("SITELENS_DATABASE_URL", f"sqlite:///{DEFAULT_DATABASE}")
    app.state.engine = make_engine(url)
    initialize_database(app.state.engine)
    app.state.ai_config = None

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/scans", response_model=ScanOut)
    async def create_scan(body: ScanRequest):
        if not body.authorized:
            raise HTTPException(400, "请先确认你拥有该网站，或已获准分析其公开技术特征。")
        try:
            page = await fetch_page(body.url)
        except TargetError as exc:
            raise HTTPException(400, str(exc)) from exc
        except (httpx.TimeoutException, TimeoutError) as exc:
            raise HTTPException(504, "网站请求超时。") from exc
        except httpx.HTTPError as exc:
            raise HTTPException(502, "无法获取网站响应。") from exc

        detections = detect(page.signals())
        with Session(app.state.engine) as session:
            scan = ScanRow(
                url=_private_url_parts_removed(page.url),
                final_url=_private_url_parts_removed(page.final_url),
                status_code=page.status_code,
                title=page.title,
                content_type=page.content_type,
                summary_json=json.dumps({"headers": page.headers, "meta": page.meta, "scripts": page.scripts, "styles": page.styles}),
            )
            session.add(scan)
            session.flush()
            for result in detections:
                technology = TechnologyRow(
                    scan_id=scan.id,
                    name=result.name,
                    category=result.category,
                    score=result.score,
                    confidence=result.confidence,
                )
                session.add(technology)
                session.flush()
                session.add_all([
                    EvidenceRow(
                        technology_id=technology.id,
                        source=item.source,
                        matched=item.matched,
                        kind=item.kind,
                        weight=item.weight,
                    ) for item in result.evidence
                ])
            session.commit()
            session.refresh(scan)
            return _scan_dict(session, scan)

    @app.get("/api/scans", response_model=list[ScanOut])
    def list_scans(limit: int = Query(default=30, ge=1, le=100), offset: int = Query(default=0, ge=0)):
        with Session(app.state.engine) as session:
            scans = session.exec(
                select(ScanRow).order_by(ScanRow.created_at.desc(), ScanRow.id.desc()).offset(offset).limit(limit)
            ).all()
            return [_scan_dict(session, scan, include_reports=False) for scan in scans]

    @app.get("/api/scans/count")
    def count_scans():
        with Session(app.state.engine) as session:
            return {"count": session.exec(select(func.count()).select_from(ScanRow)).one()}

    @app.get("/api/scans/{scan_id}", response_model=ScanOut)
    def get_scan(scan_id: int):
        with Session(app.state.engine) as session:
            scan = session.get(ScanRow, scan_id)
            if not scan:
                raise HTTPException(404, "未找到这条检测记录。")
            return _scan_dict(session, scan)

    @app.get("/api/scans/{scan_id}/evidence")
    def get_evidence(scan_id: int):
        with Session(app.state.engine) as session:
            if not session.get(ScanRow, scan_id):
                raise HTTPException(404, "未找到这条检测记录。")
            technologies = session.exec(select(TechnologyRow).where(TechnologyRow.scan_id == scan_id)).all()
            return [{"technology": item.name, "evidence": _technology_dict(session, item)["evidence"]} for item in technologies]

    @app.post("/api/scans/compare")
    def compare_scans(body: CompareRequest):
        with Session(app.state.engine) as session:
            first, second = session.get(ScanRow, body.first_scan_id), session.get(ScanRow, body.second_scan_id)
            if not first or not second:
                raise HTTPException(404, "用于对比的两条检测记录必须都存在。")
            before = [_technology_dict(session, item) for item in session.exec(select(TechnologyRow).where(TechnologyRow.scan_id == first.id)).all()]
            after = [_technology_dict(session, item) for item in session.exec(select(TechnologyRow).where(TechnologyRow.scan_id == second.id)).all()]
            normalized = lambda rows: [{"name": item["name"], "evidence": [f"{ev['source']}:{ev['matched']}" for ev in item["evidence"]]} for item in rows]
            prev = {item["name"]: set(item.get("evidence", [])) for item in normalized(before)}
            curr = {item["name"]: set(item.get("evidence", [])) for item in normalized(after)}
            common = prev.keys() & curr.keys()
            return {
                "first_scan_id": first.id, "second_scan_id": second.id,
                "newly_observed": sorted(curr.keys() - prev.keys()),
                "not_observed_now": sorted(prev.keys() - curr.keys()),
                "evidence_changed": sorted(name for name in common if prev[name] != curr[name]),
                "unchanged": sorted(name for name in common if prev[name] == curr[name]),
            }

    @app.get("/api/ai/config", response_model=AIConfigView)
    def get_ai_config():
        config = app.state.ai_config
        return {"configured": bool(config), "base_url": config.base_url if config else None, "model": config.model if config else None}

    @app.post("/api/ai/config", response_model=AIConfigView)
    def set_ai_config(body: AIConfigIn):
        try:
            validate_ai_base_url(body.base_url)
        except (ValueError, httpx.InvalidURL) as exc:
            raise HTTPException(400, str(exc)) from exc
        app.state.ai_config = body.model_copy(update={"base_url": validate_ai_base_url(body.base_url)})
        return get_ai_config()

    @app.delete("/api/ai/config", status_code=204)
    def clear_ai_config():
        app.state.ai_config = None
        return Response(status_code=204)

    @app.post("/api/ai/test")
    async def ai_test():
        config = app.state.ai_config
        if not config:
            raise HTTPException(400, "请先配置 AI 服务。")
        try:
            return {"ok": await test_ai_connection(config)}
        except (httpx.HTTPError, RuntimeError, ValueError) as exc:
            return {"ok": False, "error": str(exc)}

    @app.post("/api/ai/analyze")
    async def ai_analyze(body: AIAnalysisRequest):
        if not body.confirm_data_sent:
            raise HTTPException(400, "请先确认页面展示的分析数据，再发送到 AI 服务。")
        config = app.state.ai_config
        if not config:
            raise HTTPException(400, "请先配置 AI 服务。")
        with Session(app.state.engine) as session:
            scan = session.get(ScanRow, body.scan_id)
            if not scan:
                raise HTTPException(404, "未找到这条检测记录。")
            scan_data = _scan_dict(session, scan)
        minimized = {
            key: scan_data[key] for key in ("url", "final_url", "status_code", "title")
        }
        minimized["technologies"] = [
            {"name": tech["name"], "category": tech["category"], "confidence": tech["confidence"],
             "evidence": [{"source": ev["source"], "matched": ev["matched"]} for ev in tech["evidence"]]}
            for tech in scan_data["technologies"]
        ]
        try:
            result = await generate_ai_analysis(config, minimized)
        except (httpx.HTTPError, RuntimeError, ValueError) as exc:
            raise HTTPException(502, f"AI 分析失败：{exc}") from exc
        content = result.content
        secret = config.api_key.get_secret_value()
        if len(secret) >= 8:
            content = content.replace(secret, "[redacted]")
        with Session(app.state.engine) as session:
            report = AIReportRow(scan_id=body.scan_id, model=result.model, content=content)
            session.add(report)
            session.commit()
            session.refresh(report)
            return {"id": report.id, "model": report.model, "content": report.content, "created_at": report.created_at}

    @app.get("/api/reports")
    def list_reports(limit: int = Query(default=50, ge=1, le=100)):
        with Session(app.state.engine) as session:
            reports = session.exec(select(AIReportRow).order_by(AIReportRow.created_at.desc()).limit(limit)).all()
            return [{"id": item.id, "scan_id": item.scan_id, "model": item.model, "content": item.content, "created_at": item.created_at} for item in reports]

    @app.get("/api/reports/{report_id}")
    def get_report(report_id: int):
        with Session(app.state.engine) as session:
            report = session.get(AIReportRow, report_id)
            if not report:
                raise HTTPException(404, "未找到这份 AI 分析报告。")
            scan = session.get(ScanRow, report.scan_id)
            return {"report": {"id": report.id, "model": report.model, "content": report.content, "created_at": report.created_at}, "scan": _scan_dict(session, scan)}

    @app.get("/api/reports/{scan_id}/export")
    def export_report(scan_id: int, format: str = Query(pattern="^(html|json)$")):
        with Session(app.state.engine) as session:
            scan = session.get(ScanRow, scan_id)
            if not scan:
                raise HTTPException(404, "未找到这条检测记录。")
            data = _scan_dict(session, scan)
        if format == "json":
            return Response(json.dumps(data, ensure_ascii=False, default=str, indent=2), media_type="application/json")
        confidence_names = {"high": "高", "medium": "中", "low": "低"}
        technologies = "".join(
            f"<section><h2>{html.escape(item['name'])} <small>类别：{html.escape(item['category_label'])} · {confidence_names.get(item['confidence'], '未知')}置信等级</small></h2>"
            + "".join(f"<p><b>证据来源：{html.escape(ev['source'])}</b>：{html.escape(ev['matched'])}</p>" for ev in item["evidence"])
            + "</section>" for item in data["technologies"]
        )
        ai = "".join(f"<section><h2>AI 分析 · {html.escape(item['model'])}</h2><pre>{html.escape(item['content'])}</pre></section>" for item in data["ai_reports"])
        document = (
            "<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>SiteLens AI 检测报告</title>"
            "<style>body{font:16px system-ui;max-width:900px;margin:40px auto;background:#101720;color:#e8eef6}"
            "section{padding:18px;border:1px solid #344254;border-radius:12px;margin:16px 0}small{color:#9aabc0}pre{white-space:pre-wrap}"
            "@media print{body{background:#fff;color:#111;margin:0}section{border-color:#bbb;break-inside:avoid}small{color:#555}}</style>"
            f"<h1>网站检测报告</h1><p>检测网址：{html.escape(data['url'])} · HTTP 状态：{data['status_code']} · 检测时间：{html.escape(data['created_at'].isoformat())}</p>"
            f"<h2>{html.escape(data['title'])}</h2>{technologies}{ai}"
            "<p>识别依据为公开响应证据。置信等级是项目内部规则分数，不代表统计概率。"
            "架构关系仅为推测；本次缺少证据不代表技术已被移除。</p></html>"
        )
        return Response(document, media_type="text/html; charset=utf-8")

    frontend_dist = Path(__file__).parents[2] / "frontend" / "dist"
    if frontend_dist.is_dir():
        assets = frontend_dist / "assets"
        if assets.is_dir():
            app.mount("/assets", StaticFiles(directory=assets), name="frontend-assets")

        @app.get("/{path:path}", include_in_schema=False)
        def frontend(path: str):
            if path == "api" or path.startswith("api/"):
                raise HTTPException(404, "未找到该 API 接口。")
            return FileResponse(frontend_dist / "index.html")
    return app


app = create_app()
