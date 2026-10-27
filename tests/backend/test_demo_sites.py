from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import httpx
import pytest
from app import fetcher
from app.detector import detect
from app.security import ValidatedTarget

ROOT = Path(__file__).parents[2]


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        site = "react" if self.path == "/react" else "wordpress"
        body = (ROOT / "demo-sites" / site / "index.html").read_bytes()
        self.server_version = "nginx" if site == "react" else "Apache"
        self.sys_version = ""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@pytest.mark.asyncio
async def test_two_controlled_local_sites_through_pinned_http_transport(monkeypatch):
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]

    def local_target(value):
        url = httpx.URL(value)
        return ValidatedTarget(url, url.host, port, ("127.0.0.1",))

    monkeypatch.setattr(fetcher, "validate_target", local_target)
    try:
        react = await fetcher.fetch_page(f"http://react.demo.test:{port}/react")
        wordpress = await fetcher.fetch_page(f"http://wordpress.demo.test:{port}/wordpress")
    finally:
        server.shutdown()
        server.server_close()

    react_matches = {item.name for item in detect(react.signals())}
    wordpress_matches = {item.name for item in detect(wordpress.signals())}
    assert {"React", "Nginx"} <= react_matches
    assert {"WordPress", "Apache"} <= wordpress_matches
