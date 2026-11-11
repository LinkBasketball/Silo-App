"""Safe article-URL ingestion: SSRF protection, redirect validation, size/time limits, robots.txt."""
from __future__ import annotations

import ipaddress
import socket
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

import httpx

from app.core.config import get_settings
from app.core.errors import SiloError

ALLOWED_PORTS = {None, 80, 443}
BLOCKED_HOSTNAMES = {"localhost", "metadata.google.internal", "metadata", "instance-data"}
USER_AGENT = "SILO-civic-context/0.1 (+open-source civic research tool; respects robots.txt)"


def _ip_is_public(ip: ipaddress._BaseAddress) -> bool:
    return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast
                or ip.is_reserved or ip.is_unspecified or (ip.version == 6 and ip.ipv4_mapped
                                                           and not _ip_is_public(ip.ipv4_mapped)))


def validate_public_url(url: str, resolver=socket.getaddrinfo) -> str:
    """Reject anything that is not http(s) on a standard port resolving only to public IPs."""
    if not isinstance(url, str) or len(url) > 2048:
        raise SiloError(400, "invalid_url", "URL is missing or too long.")
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https"):
        raise SiloError(400, "invalid_url", "Only http and https URLs can be analyzed.")
    if parts.username or parts.password:
        raise SiloError(400, "invalid_url", "URLs with embedded credentials are not allowed.")
    host = (parts.hostname or "").rstrip(".").lower()
    if not host or host in BLOCKED_HOSTNAMES or host.endswith((".local", ".internal", ".localhost")):
        raise SiloError(400, "blocked_url", "That host cannot be fetched.")
    try:
        port = parts.port
    except ValueError:
        raise SiloError(400, "invalid_url", "Invalid port.") from None
    if port not in ALLOWED_PORTS:
        raise SiloError(400, "blocked_url", "Only standard web ports (80/443) are allowed.")
    try:
        literal = ipaddress.ip_address(host)
        addrs = [literal]
    except ValueError:
        try:
            infos = resolver(host, port or (443 if parts.scheme == "https" else 80), proto=socket.IPPROTO_TCP)
        except socket.gaierror:
            raise SiloError(400, "unresolvable_url", "The host name could not be resolved.") from None
        addrs = [ipaddress.ip_address(info[4][0].split("%")[0]) for info in infos]
    if not addrs or not all(_ip_is_public(a) for a in addrs):
        raise SiloError(400, "blocked_url", "That address points to a private or reserved network and cannot be fetched.")
    return parts.geturl()


class _TextExtractor(HTMLParser):
    SKIP = {"script", "style", "noscript", "nav", "footer", "header", "aside", "form", "svg"}

    def __init__(self):
        super().__init__()
        self.title, self._in_title, self._skip, self._in_p = "", False, 0, False
        self.paragraphs: list[str] = []
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
        elif tag == "title":
            self._in_title = True
        elif tag in ("p", "h1", "h2", "blockquote", "li"):
            self._in_p, self._buf = True, []

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1
        elif tag == "title":
            self._in_title = False
        elif tag in ("p", "h1", "h2", "blockquote", "li") and self._in_p:
            text = " ".join("".join(self._buf).split())
            if len(text.split()) >= 6:
                self.paragraphs.append(text)
            self._in_p = False

    def handle_data(self, data):
        if self._skip:
            return
        if self._in_title:
            self.title += data
        elif self._in_p:
            self._buf.append(data)


def _get(client: httpx.Client, url: str, max_bytes: int) -> httpx.Response | tuple:
    """Follow redirects manually so every hop is re-validated."""
    s = get_settings()
    for _ in range(s.url_fetch_max_redirects + 1):
        validate_public_url(url)
        with client.stream("GET", url) as r:
            if r.is_redirect:
                url = urljoin(url, r.headers.get("location", ""))
                continue
            body = b""
            for chunk in r.iter_bytes():
                body += chunk
                if len(body) > max_bytes:
                    raise SiloError(413, "too_large", "The page is larger than SILO's size limit.")
            return r, body, url
    raise SiloError(400, "too_many_redirects", "The URL redirected too many times.")


def fetch_article_text(url: str, transport: httpx.BaseTransport | None = None) -> dict:
    s = get_settings()
    if not s.url_fetch_enabled:
        raise SiloError(503, "url_fetch_disabled", "URL ingestion is disabled on this server. Paste the text instead.")
    url = validate_public_url(url)
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,text/plain;q=0.9"}
    try:
        with httpx.Client(timeout=s.url_fetch_timeout_s, follow_redirects=False, headers=headers, transport=transport) as c:
            parts = urlsplit(url)
            robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
            try:
                rr, rbody, _ = _get(c, robots_url, 200_000)
                if rr.status_code == 200:
                    rp = RobotFileParser()
                    rp.parse(rbody.decode("utf-8", "replace").splitlines())
                    if not rp.can_fetch(USER_AGENT, url):
                        raise SiloError(403, "robots_disallowed", "This site's robots.txt does not permit automated access. Paste the text instead.")
            except SiloError as e:
                if e.code == "robots_disallowed":
                    raise
            r, body, final_url = _get(c, url, s.url_fetch_max_bytes)
    except httpx.TimeoutException:
        raise SiloError(504, "fetch_timeout", "The site took too long to respond.") from None
    except httpx.HTTPError:
        raise SiloError(502, "fetch_failed", "The page could not be retrieved. It may be blocked, offline, or require a login.") from None
    if r.status_code in (401, 402, 403):
        raise SiloError(403, "access_restricted", "The page requires a subscription or login. SILO does not bypass access controls — paste the text you are allowed to read.")
    if r.status_code >= 400:
        raise SiloError(502, "fetch_failed", f"The site returned HTTP {r.status_code}.")
    ctype = r.headers.get("content-type", "")
    text = body.decode(r.encoding or "utf-8", "replace")
    if "html" in ctype:
        ex = _TextExtractor()
        ex.feed(text)
        title, content = ex.title.strip(), "\n\n".join(ex.paragraphs)
    elif "text/plain" in ctype:
        title, content = "", text
    else:
        raise SiloError(415, "unsupported_content", "Only HTML and plain-text pages can be analyzed.")
    if len(content.split()) < 25:
        raise SiloError(422, "no_article_text", "SILO could not find enough article text on that page. Paste the text instead.")
    return {"title": title or final_url, "text": content[: s.max_text_chars], "url": final_url}
