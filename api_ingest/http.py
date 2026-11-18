"""HTTP client: retry with exponential backoff, timeout, per-host rate limit, generic User-Agent."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from urllib.parse import urlparse

import requests

from . import config

RETRY_STATUS = {429, 500, 502, 503, 504}


@dataclass
class Response:
    url: str
    status: int | None
    content: bytes
    seconds: float
    attempts: int
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.status == 200 and self.error is None

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.content).hexdigest()


class Client:
    def __init__(self, session: requests.Session | None = None, sleep=time.sleep, clock=time.monotonic):
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": config.USER_AGENT, "Accept": "application/json"})
        self._last: dict[str, float] = {}
        self._sleep, self._clock = sleep, clock

    def _wait(self, host: str) -> None:
        gap = config.MIN_INTERVAL.get(host, 1.0)
        wait = self._last.get(host, -1e9) + gap - self._clock()
        if wait > 0:
            self._sleep(wait)
        self._last[host] = self._clock()

    def get(self, url: str, params: dict | None = None) -> Response:
        """GET with up to MAX_ATTEMPTS attempts. Never raises for network or HTTP errors: the outcome is in Response (status, error)."""
        host = urlparse(url).netloc
        t0 = self._clock()
        error, status, content = None, None, b""
        attempts = 0
        for attempts in range(1, config.MAX_ATTEMPTS + 1):
            self._wait(host)
            try:
                r = self.session.get(url, params=params, timeout=config.TIMEOUT)
                status, content, error = r.status_code, r.content, None
                if status not in RETRY_STATUS:
                    if status != 200:
                        error = f"HTTP {status}"
                    break
                error = f"HTTP {status}"
            except requests.RequestException as exc:
                status, content, error = None, b"", f"{type(exc).__name__}: {str(exc)[:200]}"
            if attempts < config.MAX_ATTEMPTS:
                self._sleep(config.BACKOFF_SECONDS * 2 ** (attempts - 1))
        return Response(url if not params else requests.Request("GET", url, params=params).prepare().url, status, content,
                        round(self._clock() - t0, 2), attempts, error)
