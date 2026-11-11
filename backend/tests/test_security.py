import socket

import httpx
import pytest

from app.core.errors import SiloError
from app.core.security import fetch_article_text, validate_public_url


def fake_resolver(ip):
    return lambda host, port, proto=0: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port))]


@pytest.mark.parametrize("url", [
    "file:///etc/passwd", "ftp://example.com/x", "gopher://x", "http://localhost/", "http://127.0.0.1/",
    "http://169.254.169.254/latest/meta-data/", "http://[::1]/", "http://10.0.0.5/", "http://192.168.1.1/",
    "http://0.0.0.0/", "http://example.com:8080/", "http://user:pass@example.com/", "http://metadata.google.internal/",
    "http://printer.local/", "http://[::ffff:127.0.0.1]/",
])
def test_blocked_urls(url):
    with pytest.raises(SiloError):
        validate_public_url(url, resolver=fake_resolver("93.184.216.34"))


def test_dns_to_private_ip_blocked():
    with pytest.raises(SiloError) as e:
        validate_public_url("https://innocent.example/", resolver=fake_resolver("10.1.2.3"))
    assert e.value.code == "blocked_url"


def test_public_url_allowed():
    assert validate_public_url("https://news.example/story", resolver=fake_resolver("93.184.216.34")).startswith("https://")


ARTICLE = "<html><head><title>Story</title></head><body><nav>menu items here and more</nav>" + \
    "".join(f"<p>Paragraph {i} explains what the council voted on and why it matters to residents today.</p>" for i in range(5)) + \
    "<script>alert(1)</script></body></html>"


def _patch_public(monkeypatch):
    import app.core.security as sec
    monkeypatch.setattr(sec, "validate_public_url", lambda url, resolver=None: url)


def test_fetch_extracts_paragraphs(monkeypatch):
    _patch_public(monkeypatch)

    def handler(req):
        if req.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(200, headers={"content-type": "text/html"}, text=ARTICLE)
    out = fetch_article_text("https://news.example/story", transport=httpx.MockTransport(handler))
    assert out["title"] == "Story" and "Paragraph 0" in out["text"]
    assert "alert" not in out["text"] and "menu" not in out["text"]


def test_redirects_are_revalidated(monkeypatch):
    import app.core.security as sec
    seen = []

    def check(url, resolver=None):
        seen.append(url)
        if "169.254" in url:
            raise SiloError(400, "blocked_url", "blocked")
        return url
    monkeypatch.setattr(sec, "validate_public_url", check)

    def handler(req):
        if req.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(302, headers={"location": "http://169.254.169.254/"})
    with pytest.raises(SiloError) as e:
        fetch_article_text("https://news.example/story", transport=httpx.MockTransport(handler))
    assert e.value.code == "blocked_url" and any("169.254" in u for u in seen)


def test_paywall_not_bypassed(monkeypatch):
    _patch_public(monkeypatch)
    t = httpx.MockTransport(lambda req: httpx.Response(404 if req.url.path == "/robots.txt" else 402))
    with pytest.raises(SiloError) as e:
        fetch_article_text("https://news.example/story", transport=t)
    assert e.value.code == "access_restricted"


def test_robots_disallow_respected(monkeypatch):
    _patch_public(monkeypatch)

    def handler(req):
        if req.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /")
        return httpx.Response(200, headers={"content-type": "text/html"}, text=ARTICLE)
    with pytest.raises(SiloError) as e:
        fetch_article_text("https://news.example/story", transport=httpx.MockTransport(handler))
    assert e.value.code == "robots_disallowed"


def test_size_limit(monkeypatch):
    _patch_public(monkeypatch)
    from app.core.config import get_settings
    monkeypatch.setattr(get_settings(), "url_fetch_max_bytes", 1000)
    t = httpx.MockTransport(lambda req: httpx.Response(404) if req.url.path == "/robots.txt"
                            else httpx.Response(200, headers={"content-type": "text/html"}, text="x" * 5000))
    with pytest.raises(SiloError) as e:
        fetch_article_text("https://news.example/story", transport=t)
    assert e.value.code == "too_large"


def test_analyze_url_blocked_via_api(client):
    r = client.post("/api/news/analyze", json={"url": "http://127.0.0.1:8000/api/health"})
    assert r.status_code == 400 and r.json()["error"]["code"] == "blocked_url"
