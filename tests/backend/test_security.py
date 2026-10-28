import socket
from types import SimpleNamespace

import pytest
from app.security import PinnedBackend, TargetError, validate_target


def resolver_for(*addresses):
    return lambda host, port, type: [
        (socket.AF_INET6 if ":" in address else socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, port))
        for address in addresses
    ]


@pytest.mark.parametrize("url", [
    "file:///etc/passwd",
    "http://user:pass@example.com/",
    "http://127.0.0.1/",
    "http://[::1]/",
])
def test_rejects_unsafe_target_urls(url):
    with pytest.raises(TargetError):
        validate_target(url, resolver=resolver_for("93.184.216.34"))


def test_rejects_hostname_with_any_private_dns_answer():
    with pytest.raises(TargetError, match="禁止检测"):
        validate_target("https://example.test", resolver=resolver_for("93.184.216.34", "10.0.0.4"))


def test_accepts_public_hostname_and_returns_pinned_addresses():
    target = validate_target("https://example.test/path", resolver=resolver_for("93.184.216.34"))
    assert target.host == "example.test"
    assert target.addresses == ("93.184.216.34",)


@pytest.mark.asyncio
async def test_pinned_backend_connects_to_checked_ip_and_rejects_host_changes():
    backend = PinnedBackend("example.test", "93.184.216.34")
    calls = []

    async def connect(host, port, **kwargs):
        calls.append((host, port))
        return "stream"

    backend.backend = SimpleNamespace(connect_tcp=connect)
    assert await backend.connect_tcp("example.test", 443) == "stream"
    assert calls == [("93.184.216.34", 443)]
    with pytest.raises(OSError):
        await backend.connect_tcp("other.test", 443)
