# brain/c4/tools/builtin eodhd_client.py 

import os
from typing import Any, Dict, Tuple

import requests


class EODHDOptionsClient:
    """
    Thin client for EODHD options API.

    Docs: https://eodhd.com/financial-apis/options-data-api/
    """

    BASE_URL = "https://eodhd.com/api/options"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("EODHD_API_KEY", "demo")

    def get_chain(self, ticker: str) -> Tuple[bool, Any]:
        """
        Fetch options chain for a ticker.

        Returns:
            (ok, data_or_error_dict)
        """
        url = f"{self.BASE_URL}/{ticker}"
        params = {
            "api_token": self.api_key,
            "fmt": "json",
        }

        try:
            resp = requests.get(url, params=params, timeout=8)
            if resp.status_code != 200:
                return False, {"error": f"http_{resp.status_code}"}

            data = resp.json()

            # EODHD usually returns {"code": "success", "data": [...]}
            if isinstance(data, dict) and data.get("code") not in (None, "success"):
                return False, {"error": "eodhd_error"}

            return True, data

        except Exception:
            return False, {"error": "request_failed"}
