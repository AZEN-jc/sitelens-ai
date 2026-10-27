import time

import httpx
import pytest
from app import fetcher
from app.security import TargetError, ValidatedTarget


@pytest.mark.asyncio
async def test_fetcher_revalidates_each_redirect_and_extracts_signals(monkeypatch):
    checked = []
    responses = iter([
        httpx.Response(302, headers={"location": "https://example.test/page"}),
        httpx.Response(200, headers={"content-type": "text/html; charset=utf-8", "server": "nginx", "set-cookie": "secret"}, text=(
            '<title>Demo</title><meta name="generator" content="WordPress">'
            '<script src="/wp-content/app.js?token=secret"></script><link rel="stylesheet" href="/site.css">'
            '<link rel="icon" href="/favicon.ico">'
        )),
    ])

    async def handler(request):
        return next(responses)

    def validate(url):
        checked.append(url)
        return ValidatedTarget(httpx.URL(url), "example.test", 443, ("93.184.216.34",))

    monkeypatch.setattr(fetcher, "validate_target", validate)
    monkeypatch.setattr(fetcher, "PinnedTransport", lambda target: httpx.MockTransport(handler))
    result = await fetcher.fetch_page("https://example.test/start")
    assert len(checked) == 2
    assert result.title == "Demo"
    assert result.headers["server"] == "nginx"
    assert "set-cookie" not in result.headers
    assert result.scripts == ["https://example.test/wp-content/app.js"]
    assert result.styles == ["https://example.test/site.css"]
    assert result.html.startswith("<title>")


@pytest.mark.asyncio
async def test_fetcher_rejects_private_redirect(monkeypatch):
    calls = []

    def validate(url):
        calls.append(url)
        if "127.0.0.1" in url:
            raise TargetError("private target")
        return ValidatedTarget(httpx.URL(url), "example.test", 443, ("93.184.216.34",))

    async def handler(request):
        return httpx.Response(302, headers={"location": "http://127.0.0.1/admin"})

    monkeypatch.setattr(fetcher, "validate_target", validate)
    monkeypatch.setattr(fetcher, "PinnedTransport", lambda target: httpx.MockTransport(handler))
    with pytest.raises(TargetError):
        await fetcher.fetch_page("https://example.test")
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_fetcher_caps_response_body(monkeypatch):
    monkeypatch.setattr(fetcher, "MAX_BODY_BYTES", 4)
    monkeypatch.setattr(fetcher, "validate_target", lambda url: ValidatedTarget(
        httpx.URL(url), "example.test", 443, ("93.184.216.34",)
    ))

    async def handler(request):
        return httpx.Response(200, headers={"content-type": "text/html"}, content=b"12345")

    monkeypatch.setattr(fetcher, "PinnedTransport", lambda target: httpx.MockTransport(handler))
    with pytest.raises(TargetError, match="5 MiB"):
        await fetcher.fetch_page("https://example.test")


@pytest.mark.asyncio
async def test_fetcher_timeout_covers_dns_resolution(monkeypatch):
    monkeypatch.setattr(fetcher, "TIMEOUT_SECONDS", 0.01)
    monkeypatch.setattr(fetcher, "validate_target", lambda url: time.sleep(0.2))
    with pytest.raises(TimeoutError):
        await fetcher.fetch_page("https://slow-dns.test")
