# brain/c4/tools/builtin/options_data_tool.py

import requests
from brain.c4.tools.base import Tool

EODHD_API = "https://eodhd.com/api/options/{ticker}?api_token={token}&fmt=json"

class OptionsDataTool(Tool):
    """
    Fetches real options chain + IV metrics from EODHD.
    """

    def __init__(self, api_token: str = None):
        super().__init__(
            name="options_data",
            description="Fetch options chain + IV metrics via EODHD"
        )
        self.api_token = api_token or "DEMO"   # safe fallback for dev

    def run(self, ticker: str, expiry: str = None):
        url = EODHD_API.format(ticker=ticker, token=self.api_token)
        resp = requests.get(url)

        if resp.status_code != 200:
            return {
                "ok": False,
                "error": f"HTTP {resp.status_code} from EODHD"
            }

        data = resp.json()

        if not isinstance(data, dict) or "data" not in data:
            return {
                "ok": False,
                "error": f"Malformed response for {ticker}"
            }

        chain = data["data"]

        # Extract simple IV metrics
        iv_values = [
            c.get("implied_volatility")
            for c in chain
            if isinstance(c.get("implied_volatility"), (int, float))
        ]

        iv_mean = sum(iv_values) / len(iv_values) if iv_values else None

        return {
            "ok": True,
            "ticker": ticker,
            "iv_mean": iv_mean,
            "contracts": chain,
        }
