from __future__ import annotations

import html
import json
import os
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from app.ai_service import generate_ai_analysis, test_ai_connection, validate_ai_base_url
from app.compare import compare_results
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


def _technology_dict(session: Session, technology: TechnologyRow) -> dict:
    evidence = session.exec(select(EvidenceRow).where(EvidenceRow.technology_id == technology.id)).all()
    return {
        "name": technology.name,
        "category": technology.category,
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
            raise HTTPException(400, "Confirm that you own or are authorized to analyze this website.")
        try:
            page = await fetch_page(body.url)
        except TargetError as exc:
            raise HTTPException(400, str(exc)) from exc
        except (httpx.TimeoutException, TimeoutError) as exc:
            raise HTTPException(504, "The website request timed out.") from exc
        except httpx.HTTPError as exc:
            raise HTTPException(502, "The website could not be fetched.") from exc

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
    def list_scans(limit: int = Query(default=30, ge=1, le=100)):
        with Session(app.state.engine) as session:
            scans = session.exec(select(ScanRow).order_by(ScanRow.created_at.desc()).limit(limit)).all()
            return [_scan_dict(session, scan, include_reports=False) for scan in scans]

    @app.get("/api/scans/{scan_id}", response_model=ScanOut)
    def get_scan(scan_id: int):
        with Session(app.state.engine) as session:
            scan = session.get(ScanRow, scan_id)
            if not scan:
                raise HTTPException(404, "Scan not found.")
            return _scan_dict(session, scan)

    @app.get("/api/scans/{scan_id}/evidence")
    def get_evidence(scan_id: int):
        with Session(app.state.engine) as session:
            if not session.get(ScanRow, scan_id):
                raise HTTPException(404, "Scan not found.")
            technologies = session.exec(select(TechnologyRow).where(TechnologyRow.scan_id == scan_id)).all()
            return [{"technology": item.name, "evidence": _technology_dict(session, item)["evidence"]} for item in technologies]

    @app.post("/api/scans/compare")
    def compare_scans(body: CompareRequest):
        with Session(app.state.engine) as session:
            first, second = session.get(ScanRow, body.first_scan_id), session.get(ScanRow, body.second_scan_id)
            if not first or not second:
                raise HTTPException(404, "Both scans must exist.")
            before = [_technology_dict(session, item) for item in session.exec(select(TechnologyRow).where(TechnologyRow.scan_id == first.id)).all()]
            after = [_technology_dict(session, item) for item in session.exec(select(TechnologyRow).where(TechnologyRow.scan_id == second.id)).all()]
            normalized = lambda rows: [{"name": item["name"], "evidence": [f"{ev['source']}:{ev['matched']}" for ev in item["evidence"]]} for item in rows]
            return {"first_scan_id": first.id, "second_scan_id": second.id, **compare_results(normalized(before), normalized(after))}

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
            raise HTTPException(400, "Configure an AI service first.")
        try:
            return {"ok": await test_ai_connection(config)}
        except (httpx.HTTPError, RuntimeError, ValueError) as exc:
            return {"ok": False, "error": str(exc)}

    @app.post("/api/ai/analyze")
    async def ai_analyze(body: AIAnalysisRequest):
        if not body.confirm_data_sent:
            raise HTTPException(400, "Confirm the displayed analysis data before sending it to the AI service.")
        config = app.state.ai_config
        if not config:
            raise HTTPException(400, "Configure an AI service first.")
        with Session(app.state.engine) as session:
            scan = session.get(ScanRow, body.scan_id)
            if not scan:
                raise HTTPException(404, "Scan not found.")
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
            raise HTTPException(502, f"AI analysis failed: {exc}") from exc
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
                raise HTTPException(404, "Report not found.")
            scan = session.get(ScanRow, report.scan_id)
            return {"report": {"id": report.id, "model": report.model, "content": report.content, "created_at": report.created_at}, "scan": _scan_dict(session, scan)}

    @app.get("/api/reports/{scan_id}/export")
    def export_report(scan_id: int, format: str = Query(pattern="^(html|json)$")):
        with Session(app.state.engine) as session:
            scan = session.get(ScanRow, scan_id)
            if not scan:
                raise HTTPException(404, "Scan not found.")
            data = _scan_dict(session, scan)
        if format == "json":
            return Response(json.dumps(data, ensure_ascii=False, default=str, indent=2), media_type="application/json")
        technologies = "".join(
            f"<section><h2>{html.escape(item['name'])} <small>{html.escape(item['category'])} · {html.escape(item['confidence'])}</small></h2>"
            + "".join(f"<p><b>{html.escape(ev['source'])}</b>: {html.escape(ev['matched'])}</p>" for ev in item["evidence"])
            + "</section>" for item in data["technologies"]
        )
        ai = "".join(f"<section><h2>AI analysis · {html.escape(item['model'])}</h2><pre>{html.escape(item['content'])}</pre></section>" for item in data["ai_reports"])
        document = (
            "<!doctype html><meta charset='utf-8'><title>SiteLens report</title>"
            "<style>body{font:16px system-ui;max-width:900px;margin:40px auto;background:#101720;color:#e8eef6}"
            "section{padding:18px;border:1px solid #344254;border-radius:12px;margin:16px 0}small{color:#9aabc0}pre{white-space:pre-wrap}"
            "@media print{body{background:#fff;color:#111;margin:0}section{border-color:#bbb;break-inside:avoid}small{color:#555}}</style>"
            f"<h1>Website analysis</h1><p>{html.escape(data['url'])} · HTTP {data['status_code']} · {html.escape(data['created_at'].isoformat())}</p>"
            f"<h2>{html.escape(data['title'])}</h2>{technologies}{ai}"
            "<p>Evidence comes from publicly observable responses. Confidence is an internal rule score, not a probability."
            " Architecture relationships are hypotheses; missing evidence does not prove technology removal.</p>"
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
                raise HTTPException(404, "API endpoint not found.")
            return FileResponse(frontend_dist / "index.html")
    return app


app = create_app()
