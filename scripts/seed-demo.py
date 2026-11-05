#!/usr/bin/env python3
"""Add two offline demo scans from the bundled controlled pages."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from sqlmodel import Session, select

from app.database import initialize_database, make_engine
from app.detector import detect
from app.fetcher import parse_snapshot
from app.models import EvidenceRow, ScanRow, TechnologyRow

DEMO_SITES = (
    ("wordpress", "https://wordpress.demo.test/", "Apache"),
    ("react", "https://react.demo.test/", "nginx"),
)
MARKER = "demo.test"


def build_snapshot(site: str, url: str, server: str):
    body = (ROOT / "demo-sites" / site / "index.html").read_bytes()
    return parse_snapshot(
        url,
        url,
        200,
        {"Content-Type": "text/html; charset=utf-8", "Server": server},
        body,
    )


def main() -> int:
    url = os.getenv("SITELENS_DATABASE_URL", f"sqlite:///{ROOT / 'data' / 'sitelens.sqlite'}")
    engine = make_engine(url)
    initialize_database(engine)
    with Session(engine) as session:
        existing = [row for row in session.exec(select(ScanRow)).all() if MARKER in row.url]
        if existing:
            print(f"演示数据已存在，跳过（{len(existing)} 条）。")
            return 0
        for site, page_url, server in DEMO_SITES:
            page = build_snapshot(site, page_url, server)
            signals = page.signals()
            stored = {key: value for key, value in signals.items() if key != "html"}
            scan = ScanRow(
                url=page_url,
                final_url=page_url,
                status_code=200,
                title=page.title,
                content_type=page.content_type,
                summary_json=json.dumps(stored, ensure_ascii=False),
            )
            session.add(scan)
            session.flush()
            for hit in detect(signals):
                technology = TechnologyRow(
                    scan_id=scan.id,
                    name=hit.name,
                    category=hit.category,
                    score=hit.score,
                    confidence=hit.confidence,
                )
                session.add(technology)
                session.flush()
                for item in hit.evidence:
                    session.add(EvidenceRow(
                        technology_id=technology.id,
                        source=item.source,
                        matched=item.matched,
                        kind=item.kind,
                        weight=item.weight,
                    ))
        session.commit()
    print("已写入 2 条离线演示检测记录。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
