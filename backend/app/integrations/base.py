"""Shared adapter behaviour: timeouts, bounded retries with exponential backoff, rate-limit
handling, response validation and provenance. Adapters never raise raw HTTP errors to callers."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import UTC, datetime

import httpx

from app.core.config import get_settings


class AdapterError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


@dataclass
class AdapterStatus:
    name: str
    configured: bool
    enabled: bool
    last_success_at: datetime | None = None
    last_error: str | None = None
    extra: dict = field(default_factory=dict)


class BaseAdapter:
    name = "base"
    base_url = ""
    key_param = "api_key"
    docs_url = ""

    def __init__(self, api_key: str | None, base_url: str | None = None,
                 transport: httpx.BaseTransport | None = None, sleep=time.sleep):
        s = get_settings()
        self.api_key = api_key
        self.base_url = (base_url or self.base_url).rstrip("/")
        self.timeout = s.external_timeout_s
        self.max_retries = s.external_max_retries
        self._transport = transport
        self._sleep = sleep
        self.status = AdapterStatus(self.name, configured=bool(api_key), enabled=s.live_data_enabled)

    def _require_ready(self):
        if not self.status.enabled:
            raise AdapterError("live_disabled", "Live data is disabled on this server (SILO_LIVE_DATA_ENABLED=false).")
        if not self.api_key:
            raise AdapterError("not_configured", f"No API key configured for {self.name}.")

    def get_json(self, path: str, params: dict | None = None) -> dict:
        self._require_ready()
        params = {**(params or {}), self.key_param: self.api_key}
        url = f"{self.base_url}/{path.lstrip('/')}"
        delay = 0.5
        last: Exception | None = None
        with httpx.Client(timeout=self.timeout, transport=self._transport) as client:
            for attempt in range(self.max_retries + 1):
                try:
                    r = client.get(url, params=params, headers={"Accept": "application/json"})
                except httpx.TimeoutException as e:
                    last = e
                except httpx.HTTPError as e:
                    last = e
                else:
                    if r.status_code == 429 or r.status_code >= 500:
                        last = AdapterError("upstream_unavailable", f"{self.name} returned HTTP {r.status_code}")
                        retry_after = r.headers.get("retry-after")
                        if retry_after and retry_after.isdigit():
                            delay = min(float(retry_after), 10.0)
                    elif r.status_code in (401, 403):
                        self.status.last_error = "unauthorized"
                        raise AdapterError("unauthorized", f"{self.name} rejected the API key.")
                    elif r.status_code >= 400:
                        self.status.last_error = f"http_{r.status_code}"
                        raise AdapterError("bad_request", f"{self.name} returned HTTP {r.status_code}.")
                    else:
                        try:
                            data = r.json()
                        except ValueError:
                            raise AdapterError("invalid_response", f"{self.name} returned non-JSON data.") from None
                        if not isinstance(data, dict):
                            raise AdapterError("invalid_response", f"{self.name} returned an unexpected shape.")
                        self.status.last_success_at = datetime.now(UTC)
                        self.status.last_error = None
                        return data
                if attempt < self.max_retries:
                    self._sleep(delay)
                    delay *= 2
        self.status.last_error = type(last).__name__ if last else "unknown"
        raise AdapterError("upstream_unavailable", f"{self.name} could not be reached after {self.max_retries + 1} attempts.")

    def provenance(self, url: str) -> dict:
        return {"source_name": self.name, "source_url": url, "data_status": "live",
                "retrieved_at": datetime.now(UTC).isoformat()}
