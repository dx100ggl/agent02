# brain/c4/bools/builtin/yahoo_client.py

import requests
from typing import Any, Dict, Tuple

class YahooOptionsClient:
    BASE_URL = "https://query2.finance.yahoo.com/v7/finance/options"

    def get_chain(self, ticker: str) -> Tuple[bool, Any]:
        """
        Fetch options chain from Yahoo Finance.
        Returns (ok, data_or_error).
        """
        url = f"{self.BASE_URL}/{ticker}"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code != 200:
                return False, {"error": f"http_{resp.status_code}"}
            return True, resp.json()
        except Exception:
            return False, {"error": "request_failed"}
