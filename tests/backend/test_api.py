from dataclasses import replace

import httpx
import pytest
from app import main
from app.fetcher import PageSnapshot
from app.schemas import AIAnalysisResult


def page(title, server, scripts=()):
    return PageSnapshot(
        url="https://example.test", final_url="https://example.test/", status_code=200,
        content_type="text/html", title=title, headers={"server": server, "content-type": "text/html"},
        meta=[], scripts=list(scripts), styles=[], html="",
    )


@pytest.mark.asyncio
async def test_scan_history_evidence_compare_and_report(tmp_path, monkeypatch):
    responses = iter([page("First", "nginx"), page("Second", "Apache")])
    async def fetch(url):
        return next(responses)
    monkeypatch.setattr(main, "fetch_page", fetch)
    app = main.create_app(f"sqlite:///{tmp_path / 'test.db'}")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        first = await client.post("/api/scans", json={"url": "https://example.test", "authorized": True})
        second = await client.post("/api/scans", json={"url": "https://example.test", "authorized": True})
        assert first.status_code == second.status_code == 200
        first_data, second_data = first.json(), second.json()
        assert first_data["title"] == "First"
        assert first_data["technologies"][0]["name"] == "Nginx"
        evidence = await client.get(f"/api/scans/{first_data['id']}/evidence")
        assert evidence.json()
        comparison_response = await client.post("/api/scans/compare", json={
            "first_scan_id": first_data["id"], "second_scan_id": second_data["id"]
        })
        comparison = comparison_response.json()
        assert comparison["not_observed_now"] == ["Nginx"]
        exported = await client.get(f"/api/reports/{first_data['id']}/export?format=json")
        assert exported.status_code == 200
        assert "Nginx" in exported.text
        assert "html" not in exported.json()


@pytest.mark.asyncio
async def test_escapes_report_html(tmp_path, monkeypatch):
    async def fetch(url):
        return replace(page("<script>alert(1)</script>", "nginx"), url=url, final_url=url)
    monkeypatch.setattr(main, "fetch_page", fetch)
    app = main.create_app(f"sqlite:///{tmp_path / 'escape.db'}")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        scan = await client.post("/api/scans", json={"url": "https://example.test/?token=secret"})
        assert "token=secret" not in scan.json()["url"]
        report = await client.get(f"/api/reports/{scan.json()['id']}/export?format=html")
        assert "<script>alert(1)</script>" not in report.text
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in report.text
        assert "网站检测报告" in report.text
        assert "公开响应证据" in report.text
        assert "类别：Web 服务器" in report.text
        assert "类别：Web server" not in report.text
        assert "token=secret" not in report.text


@pytest.mark.asyncio
async def test_ai_key_is_memory_only_and_never_returned(tmp_path, monkeypatch):
    async def test_connection(config):
        return True
    async def generate(config, scan):
        return AIAnalysisResult(model=config.model, content="Evidence-based summary secret-value")
    monkeypatch.setattr(main, "test_ai_connection", test_connection)
    monkeypatch.setattr(main, "generate_ai_analysis", generate)
    async def fetch(url):
        return page("AI Test", "nginx")
    monkeypatch.setattr(main, "fetch_page", fetch)
    app = main.create_app(f"sqlite:///{tmp_path / 'ai.db'}")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        configured = await client.post("/api/ai/config", json={
            "base_url": "http://127.0.0.1:11434/v1", "api_key": "secret-value", "model": "local-model"
        })
        assert configured.status_code == 200
        status = await client.get("/api/ai/config")
        assert "secret-value" not in status.text
        tested = await client.post("/api/ai/test")
        assert tested.json()["ok"] is True
        scan = await client.post("/api/scans", json={"url": "https://example.test", "authorized": True})
        assert scan.status_code == 200
        scan_id = scan.json()["id"]
        denied = await client.post("/api/ai/analyze", json={"scan_id": scan_id, "confirm_data_sent": False})
        assert denied.status_code == 400
        analyzed = await client.post("/api/ai/analyze", json={"scan_id": scan_id, "confirm_data_sent": True})
        assert analyzed.status_code == 200
        assert "secret-value" not in analyzed.text
        assert "[redacted]" in analyzed.json()["content"]
        history = await client.get("/api/scans")
        assert history.json()[0]["ai_report_count"] == 1
        assert history.json()[0]["ai_reports"] == []
        detail = await client.get(f"/api/scans/{scan_id}")
        assert detail.json()["ai_reports"][0]["content"] == "Evidence-based summary [redacted]"
        cleared = await client.delete("/api/ai/config")
        assert cleared.status_code == 204
        status = await client.get("/api/ai/config")
        assert status.json()["configured"] is False


@pytest.mark.asyncio
async def test_scan_history_count_and_offset_reach_older_records(tmp_path, monkeypatch):
    async def fetch(url):
        return page("History", "nginx")

    monkeypatch.setattr(main, "fetch_page", fetch)
    app = main.create_app(f"sqlite:///{tmp_path / 'history-pages.db'}")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        created = []
        for index in range(35):
            response = await client.post("/api/scans", json={
                "url": f"https://example.test/{index}", "authorized": True,
            })
            created.append(response.json()["id"])

        count = await client.get("/api/scans/count")
        first_page = await client.get("/api/scans?limit=30&offset=0")
        second_page = await client.get("/api/scans?limit=30&offset=30")

    assert count.json() == {"count": 35}
    assert len(first_page.json()) == 30
    assert len(second_page.json()) == 5
    assert {scan["id"] for scan in first_page.json() + second_page.json()} == set(created)
