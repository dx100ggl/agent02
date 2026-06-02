import time
from typing import Any, Dict, Tuple

import os
import requests


class PolygonOptionsClient:
    BASE_URL = "https://api.polygon.io"

    def __init__(self, api_key: str | None = None, timeout: float = 5.0, max_retries: int = 2):
        self.api_key = api_key or os.getenv("POLYGON_API_KEY", "")
        self.timeout = timeout
        self.max_retries = max_retries

    def _request(self, path: str, params: Dict[str, Any]) -> Tuple[bool, Any]:
        """Safe request wrapper. Never raises. Returns (ok, data_or_error)."""
        if not self.api_key:
            return False, {"error": "missing_api_key"}

        url = f"{self.BASE_URL}{path}"
        params = dict(params or {})
        params["apiKey"] = self.api_key

        for attempt in range(self.max_retries + 1):
            try:
                resp = requests.get(url, params=params, timeout=self.timeout)
                status = resp.status_code

                if status == 429:
                    # rate limit → backoff and retry
                    time.sleep(0.5 * (attempt + 1))
                    continue

                if 200 <= status < 300:
                    return True, resp.json()

                # non‑retryable 4xx
                if 400 <= status < 500:
                    return False, {"error": f"http_{status}", "body": resp.text}

                # retryable 5xx
                time.sleep(0.3 * (attempt + 1))

            except Exception:
                time.sleep(0.2 * (attempt + 1))

        return False, {"error": "request_failed"}

    # --- Public API ---------------------------------------------------------

    def get_snapshot_chain(self, ticker: str) -> Tuple[bool, Any]:
        """
        Snapshot options chain for underlying ticker.
        """
        # Polygon expects underlying symbol, e.g. "AAPL"
        return self._request(f"/v3/snapshot/options/{ticker}", params={})
