"""Small in-process sliding-window limiter for expensive POST endpoints.

Suitable for a single worker. Multi-worker deployments should put a shared limiter
(e.g. at the reverse proxy) in front of the API; see docs/SECURITY.md.
"""
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Request

from app.core.config import get_settings
from app.core.errors import SiloError

_hits: dict[str, deque] = defaultdict(deque)
_lock = Lock()


def rate_limit(request: Request) -> None:
    limit = get_settings().rate_limit_per_minute
    if limit <= 0:
        return
    key = request.client.host if request.client else "unknown"
    now = time.monotonic()
    with _lock:
        q = _hits[key]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= limit:
            raise SiloError(429, "rate_limited", "Too many analysis requests. Please wait a minute and try again.")
        q.append(now)


def reset() -> None:
    with _lock:
        _hits.clear()
