#!/usr/bin/env python3
"""Zero-dependency offline demo server for the defense venue.

Only the Python standard library is required. The built frontend and real
demo scans are packed in demo/site.zip and demo/scans.json. No network
requests are made, so the whole demo works without internet access.

Usage: python3 scripts/serve-offline.py [--port 8010]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import mimetypes
import sys
import webbrowser
import zipfile
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "demo"
SCANS = json.loads((DEMO / "scans.json").read_text(encoding="utf-8"))
BY_ID = {item["id"]: item for item in SCANS}

# The report renderer is a copy of backend/app/report.py so the offline pack
# is self-contained. Load it by path to avoid importing the backend package.
_spec = importlib.util.spec_from_file_location("offline_report", DEMO / "report.py")
_report = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_report)
render_html_report = _report.render_html_report


def _report_data(scan: dict) -> dict:
    data = dict(scan)
    created = data["created_at"]
    if isinstance(created, str):
        # Python 3.10 的 fromisoformat 不认 Z 后缀，答辩机房可能用旧版本
        data["created_at"] = datetime.fromisoformat(created.replace("Z", "+00:00"))  # noqa: FURB162
    return data


def _compare(first_id: int, second_id: int) -> dict:
    def normalized(scan: dict) -> dict[str, set[str]]:
        return {
            item["name"]: {f"{ev['source']}:{ev['matched']}" for ev in item["evidence"]}
            for item in scan["technologies"]
        }
    prev, curr = normalized(BY_ID[first_id]), normalized(BY_ID[second_id])
    common = prev.keys() & curr.keys()
    return {
        "first_scan_id": first_id,
        "second_scan_id": second_id,
        "newly_observed": sorted(curr.keys() - prev.keys()),
        "not_observed_now": sorted(prev.keys() - curr.keys()),
        "evidence_changed": sorted(name for name in common if prev[name] != curr[name]),
        "unchanged": sorted(name for name in common if prev[name] == curr[name]),
    }


class Handler(BaseHTTPRequestHandler):
    site_zip: zipfile.ZipFile

    def log_message(self, format: str, *args) -> None:
        if "/assets/" not in self.path:
            sys.stderr.write("  %s\n" % (format % args))

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: object) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8"),
                   "application/json; charset=utf-8")

    def _html(self, status: int, text: str) -> None:
        self._send(status, text.encode("utf-8"), "text/html; charset=utf-8")

    def _static(self, path: str) -> None:
        name = path.lstrip("/") or "index.html"
        try:
            body = self.site_zip.read(name)
        except KeyError:
            if "." not in name.rsplit("/", 1)[-1]:
                name = "index.html"  # SPA deep link, keep the HTML content type
                body = self.site_zip.read(name)
            else:
                self._json(404, {"detail": "未找到这个静态文件。"})
                return
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in {"application/javascript", "application/json"}:
            ctype += "; charset=utf-8"
        self._send(200, body, ctype)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path, query = parsed.path, parse_qs(parsed.query)
        if path == "/api/health":
            return self._json(200, {"status": "ok"})
        if path == "/api/scans/count":
            return self._json(200, {"count": len(SCANS)})
        if path == "/api/scans":
            limit = max(1, min(100, int(query.get("limit", ["30"])[0])))
            offset = max(0, int(query.get("offset", ["0"])[0]))
            return self._json(200, SCANS[offset:offset + limit])
        if path.startswith("/api/scans/"):
            scan = BY_ID.get(int(path.rsplit("/", 1)[-1]))
            return self._json(200, scan) if scan else self._json(404, {"detail": "未找到这条检测记录。"})
        if path.startswith("/api/reports/") and path.endswith("/export"):
            scan_id = int(path.split("/")[3])
            scan = BY_ID.get(scan_id)
            if not scan:
                return self._json(404, {"detail": "未找到这条检测记录。"})
            if query.get("format", ["html"])[0] == "json":
                return self._json(200, scan)
            return self._html(200, render_html_report(_report_data(scan)))
        if path == "/api/reports":
            return self._json(200, [])
        if path == "/api/ai/config":
            return self._json(200, {"configured": False})
        return self._static(path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length) or b"{}") if length else {}
        if parsed.path == "/api/scans":
            return self._json(400, {"detail": "离线演示包不发起外部请求，请查看已预置的演示记录；完整环境请用 ./scripts/start.sh。"})
        if parsed.path == "/api/scans/compare":
            first, second = body.get("first_scan_id"), body.get("second_scan_id")
            if first not in BY_ID or second not in BY_ID:
                return self._json(404, {"detail": "用于对比的两条检测记录必须都存在。"})
            return self._json(200, _compare(first, second))
        if parsed.path == "/api/ai/test":
            return self._json(200, {"ok": False, "error": "离线演示包不连接外部 AI 服务。"})
        return self._json(400, {"detail": "离线演示包为只读模式，不保存配置或分析结果。"})

    def do_DELETE(self) -> None:
        self._send(204, b"", "application/json")


def main() -> int:
    parser = argparse.ArgumentParser(description="SiteLens 离线答辩演示服务")
    parser.add_argument("--port", type=int, default=8010)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if not (DEMO / "site.zip").is_file() or not (DEMO / "scans.json").is_file():
        print("缺少 demo/site.zip 或 demo/scans.json，请先在项目根目录运行 pnpm build。")
        return 1
    Handler.site_zip = zipfile.ZipFile(DEMO / "site.zip")
    url = f"http://127.0.0.1:{args.port}/"
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        print(f"离线演示已启动（零依赖、断网可用）：{url}")
        print(f"已载入 {len(SCANS)} 条真实演示记录。按 Ctrl+C 停止。")
        if not args.no_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
