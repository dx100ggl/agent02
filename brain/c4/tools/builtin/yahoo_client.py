# brain/c4/bools/builtin/yahoo_client.py
import requests
from typing import Any, Dict, Tuple

class YahooOptionsClient:
    BASE_URL = "https://query2.finance.yahoo.com/v7/finance/options"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://finance.yahoo.com/",
        "Cookie": "B=12345; PRF=t%3DAAPL",  # dummy cookie helps bypass 999
    }

    def get_chain(self, ticker: str) -> Tuple[bool, Any]:
        url = f"{self.BASE_URL}/{ticker}"

        try:
            resp = requests.get(url, headers=self.HEADERS, timeout=8)

            # Yahoo returns 999 or 403 when blocked
            if resp.status_code != 200:
                return False, {"error": f"http_{resp.status_code}"}

            data = resp.json()

            # Yahoo sometimes returns {"optionChain":{"error":...}}
            if data.get("optionChain", {}).get("error"):
                return False, {"error": "yahoo_chain_error"}

            return True, data

        except Exception:
            return False, {"error": "request_failed"}
