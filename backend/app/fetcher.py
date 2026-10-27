from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

from app.security import (
    MAX_BODY_BYTES,
    MAX_REDIRECTS,
    TIMEOUT_SECONDS,
    PinnedTransport,
    TargetError,
    validate_target,
)

ALLOWED_HEADERS = {"server", "content-type", "x-powered-by", "cf-ray", "via"}
PUBLIC_META_NAMES = {"generator", "application-name", "robots", "viewport", "og:site_name", "twitter:card"}


@dataclass(frozen=True)
class PageSnapshot:
    url: str
    final_url: str
    status_code: int
    content_type: str
    title: str
    headers: dict[str, str]
    meta: list[dict[str, str]]
    scripts: list[str]
    styles: list[str]
    html: str

    def signals(self):
        return {
            "headers": self.headers,
            "meta": self.meta,
            "scripts": self.scripts,
            "styles": self.styles,
            "html": self.html,
        }


def _resource_urls(soup: BeautifulSoup, final_url: str, tag: str, attribute: str, stylesheet: bool = False) -> list[str]:
    result = []
    for element in soup.find_all(tag):
        if stylesheet and "stylesheet" not in element.get("rel", []):
            continue
        value = element.get(attribute)
        if not isinstance(value, str):
            continue
        url = httpx.URL(final_url).join(value.strip())
        if url.scheme in {"http", "https"} and url.host and not url.userinfo:
            result.append(str(url.copy_with(query=None, fragment=None)))
    return list(dict.fromkeys(result))


def _clean_html_body(content: bytes, content_type: str) -> str:
    if "text/html" not in content_type.lower():
        return ""
    charset = "utf-8"
    for part in content_type.split(";")[1:]:
        name, separator, value = part.strip().partition("=")
        if separator and name.lower() == "charset":
            charset = value.strip(' "\'')
            break
    try:
        return content.decode(charset, errors="replace")
    except LookupError:
        return content.decode("utf-8", errors="replace")


def parse_snapshot(url: str, final_url: str, status_code: int, headers: dict[str, str], content: bytes) -> PageSnapshot:
    safe_headers = {key.lower(): value[:500] for key, value in headers.items() if key.lower() in ALLOWED_HEADERS}
    content_type = safe_headers.get("content-type", "")
    html = _clean_html_body(content, content_type)
    soup = BeautifulSoup(html, "html.parser")
    meta = []
    for tag in soup.find_all("meta"):
        key = str(tag.get("name") or tag.get("property") or "").strip()[:80]
        value = str(tag.get("content") or "").strip()[:240]
        if key.lower() in PUBLIC_META_NAMES and value:
            meta.append({"name": key, "content": value})
    return PageSnapshot(
        url=url,
        final_url=final_url,
        status_code=status_code,
        content_type=content_type,
        title=(soup.title.get_text(" ", strip=True)[:300] if soup.title else ""),
        headers=safe_headers,
        meta=meta,
        scripts=_resource_urls(soup, final_url, "script", "src"),
        styles=_resource_urls(soup, final_url, "link", "href", stylesheet=True),
        html=html,
    )


async def fetch_page(value: str) -> PageSnapshot:
    async with asyncio.timeout(TIMEOUT_SECONDS):
        return await _fetch_page(value)


async def _fetch_page(value: str) -> PageSnapshot:
    current = value.strip()
    original = current
    for redirect_count in range(MAX_REDIRECTS + 1):
        target = await asyncio.to_thread(validate_target, current)
        timeout = httpx.Timeout(TIMEOUT_SECONDS)
        async with httpx.AsyncClient(
            transport=PinnedTransport(target), timeout=timeout, trust_env=False,
            follow_redirects=False,
        ) as client, client.stream(
            "GET", target.url,
            headers={"User-Agent": "SiteLensAI/0.1 (+authorized public technology analysis)", "Accept-Encoding": "identity"},
        ) as response:
            if response.status_code in {301, 302, 303, 307, 308}:
                location = response.headers.get("location")
                if not location:
                    raise TargetError("The website returned a redirect without a destination.")
                if redirect_count == MAX_REDIRECTS:
                    raise TargetError("The website exceeded the redirect limit.")
                current = str(target.url.join(location))
                continue
            body = bytearray()
            async for chunk in response.aiter_bytes():
                body.extend(chunk)
                if len(body) > MAX_BODY_BYTES:
                    raise TargetError("The website response exceeded the 5 MiB scan limit.")
            headers = dict(response.headers)
            status = response.status_code
            final_url = str(target.url)
        return parse_snapshot(original, final_url, status, headers, bytes(body))
    raise TargetError("The website exceeded the redirect limit.")
