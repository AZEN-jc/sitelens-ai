import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from app.ai_service import generate_ai_analysis, validate_ai_base_url
from app.ai_service import test_ai_connection as check_ai_connection
from app.schemas import AIConfigIn


def test_ai_endpoint_allows_explicit_local_services():
    assert validate_ai_base_url("http://127.0.0.1:11434/v1/") == "http://127.0.0.1:11434/v1"


@pytest.mark.parametrize("value", [
    "file:///etc/passwd",
    "https://user:password@example.com/v1",
    "https://example.com/v1?token=secret",
    "https://example.com/v1#fragment",
])
def test_ai_endpoint_rejects_credential_and_non_http_urls(value):
    with pytest.raises(ValueError):
        validate_ai_base_url(value)


@pytest.mark.asyncio
async def test_configured_local_ai_receives_key_only_in_auth_header():
    observed = {}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            observed["path"] = self.path
            observed["authorization"] = self.headers.get("Authorization")
            observed["body"] = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            payload = json.dumps({"choices": [{"message": {"content": "Grounded analysis."}}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    Thread(target=server.serve_forever, daemon=True).start()
    config = AIConfigIn(
        base_url=f"http://127.0.0.1:{server.server_address[1]}/v1",
        api_key="local-test-secret",
        model="local-demo",
    )
    try:
        assert await check_ai_connection(config)
        result = await generate_ai_analysis(config, {
            "url": "https://example.test",
            "technologies": [{"name": "React", "evidence": [{"source": "html", "matched": "data-reactroot"}]}],
        })
    finally:
        server.shutdown()
        server.server_close()
    assert result.content == "Grounded analysis."
    assert observed["path"] == "/v1/chat/completions"
    assert observed["authorization"] == "Bearer local-test-secret"
    assert "local-test-secret" not in json.dumps(observed["body"])
