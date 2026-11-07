#!/usr/bin/env python3
"""Pre-scan well-known sites so the demo works without live network access.

Idempotent: sites already present in the database are skipped. Re-run any
time a network connection is available to refresh the showcase records."""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from sqlmodel import Session, select

from app.database import initialize_database, make_engine
from app.detector import detect
from app.fetcher import fetch_page
from app.models import EvidenceRow, ScanRow, TechnologyRow

SHOWCASE = (
    "https://wordpress.org",
    "https://www.bilibili.com",
    "https://www.jd.com",
    "https://sspai.com",
    "https://www.sohu.com",
    "https://www.csdn.net",
)


def store_scan(session: Session, page) -> None:
    signals = page.signals()
    stored = {key: value for key, value in signals.items() if key != "html"}
    scan = ScanRow(
        url=page.url,
        final_url=page.final_url,
        status_code=page.status_code,
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


async def main_async() -> int:
    url = os.getenv("SITELENS_DATABASE_URL", f"sqlite:///{ROOT / 'data' / 'sitelens.sqlite'}")
    engine = make_engine(url)
    initialize_database(engine)
    done, failed = 0, 0
    with Session(engine) as session:
        known = {row.url.rstrip("/") for row in session.exec(select(ScanRow)).all()}
        for target in SHOWCASE:
            if target.rstrip("/") in known:
                print(f"跳过（已有记录）：{target}")
                continue
            try:
                page = await fetch_page(target)
            except Exception as exc:
                print(f"× {target} 请求失败：{type(exc).__name__} {str(exc)[:60]}")
                failed += 1
                continue
            store_scan(session, page)
            session.commit()
            done += 1
            print(f"✔ {target} 已存为演示记录")
    print(f"完成：新增 {done} 条，失败 {failed} 条。")
    return 0


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
