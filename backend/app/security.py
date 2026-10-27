from __future__ import annotations

import ipaddress
import socket
from collections.abc import Callable
from dataclasses import dataclass

import httpcore
import httpx

MAX_BODY_BYTES = 5 * 1024 * 1024
MAX_REDIRECTS = 5
TIMEOUT_SECONDS = 10


class TargetError(ValueError):
    """A target is invalid or outside the public-network scan boundary."""


@dataclass(frozen=True)
class ValidatedTarget:
    url: httpx.URL
    host: str
    port: int
    addresses: tuple[str, ...]


def validate_target(
    value: str,
    *,
    resolver: Callable = socket.getaddrinfo,
) -> ValidatedTarget:
    try:
        url = httpx.URL(value.strip())
    except (httpx.InvalidURL, ValueError) as exc:
        raise TargetError("Enter a valid website URL.") from exc
    if url.scheme not in {"http", "https"} or not url.host or url.userinfo:
        raise TargetError("Only HTTP(S) URLs without embedded credentials are allowed.")

    host = url.host.lower()
    try:
        port = url.port or (443 if url.scheme == "https" else 80)
    except ValueError as exc:
        raise TargetError("The target URL contains an invalid port.") from exc
    if not 1 <= port <= 65535:
        raise TargetError("The target URL contains an invalid port.")
    try:
        literal = ipaddress.ip_address(host)
        answers = [str(literal)]
    except ValueError:
        try:
            records = resolver(host, port, type=socket.SOCK_STREAM)
            answers = list(dict.fromkeys(record[4][0].split("%", 1)[0] for record in records))
        except (OSError, ValueError) as exc:
            raise TargetError("The target hostname could not be resolved.") from exc
    if not answers:
        raise TargetError("The target hostname has no address.")
    try:
        addresses = tuple(str(ipaddress.ip_address(address)) for address in answers)
    except ValueError as exc:
        raise TargetError("The target hostname resolved to an invalid address.") from exc
    if any(not ipaddress.ip_address(address).is_global for address in addresses):
        raise TargetError("Targets resolving to private, local, or reserved addresses are blocked.")
    return ValidatedTarget(url=url, host=host, port=port, addresses=addresses)


class PinnedBackend(httpcore.AsyncNetworkBackend):
    """Connect to the validated IP while httpcore retains the URL host for TLS SNI."""

    def __init__(self, host: str, address: str):
        self.host = host.lower()
        self.address = address
        self.backend = httpcore.AnyIOBackend()

    async def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        if host.lower() != self.host:
            raise OSError("Connection host changed after target validation.")
        return await self.backend.connect_tcp(
            self.address,
            port,
            timeout=timeout,
            local_address=local_address,
            socket_options=socket_options,
        )

    async def connect_unix_socket(self, path, timeout=None, socket_options=None):
        raise OSError("Unix sockets are not allowed for website scans.")

    async def sleep(self, seconds):
        await self.backend.sleep(seconds)


class _CoreResponseStream(httpx.AsyncByteStream):
    def __init__(self, stream, pool):
        self.stream = stream
        self.pool = pool

    async def __aiter__(self):
        async for chunk in self.stream:
            yield chunk

    async def aclose(self):
        await self.stream.aclose()
        await self.pool.aclose()


class PinnedTransport(httpx.AsyncBaseTransport):
    def __init__(self, target: ValidatedTarget):
        self.pool = httpcore.AsyncConnectionPool(
            network_backend=PinnedBackend(target.host, target.addresses[0]),
            max_connections=1,
            max_keepalive_connections=0,
        )

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        core_request = httpcore.Request(
            method=request.method,
            url=httpcore.URL(
                scheme=request.url.raw_scheme,
                host=request.url.raw_host,
                port=request.url.port,
                target=request.url.raw_path,
            ),
            headers=request.headers.raw,
            content=await request.aread(),
            extensions=request.extensions,
        )
        response = await self.pool.handle_async_request(core_request)
        return httpx.Response(
            status_code=response.status,
            headers=response.headers,
            stream=_CoreResponseStream(response.stream, self.pool),
            extensions=response.extensions,
            request=request,
        )

    async def aclose(self):
        await self.pool.aclose()
