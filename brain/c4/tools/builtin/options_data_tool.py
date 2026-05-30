# brain/c4/tools/builtin/options_data_tool.py

import requests
import math
from datetime import datetime
from brain.c4.tools.base import Tool

EODHD_API = "https://eodhd.com/api/options/{ticker}?api_token={token}&fmt=json"


class OptionsDataTool(Tool):
    """
    Fetches real options chain + IV metrics from EODHD.
    Computes:
      - ATM IV
      - IV surface (per strike)
      - 1-day implied move
      - 1-week implied move
      - Skew (25-delta risk reversal)
      - Term structure (near vs next expiry)
    """

    def __init__(self, api_token: str = None):
        super().__init__(
            name="options_data",
            description="Fetch options chain + IV metrics via EODHD"
        )
        self.api_token = api_token or "DEMO"

    # ---------------------------------------------------------
    # Utility: compute implied move from IV
    # ---------------------------------------------------------
    def _implied_move(self, iv: float, days: int) -> float:
        if not iv or iv <= 0:
            return None
        return iv * math.sqrt(days / 365)

    # ---------------------------------------------------------
    # Utility: extract ATM IV
    # ---------------------------------------------------------
    def _atm_iv(self, chain, underlying_price):
        closest = None
        min_diff = float("inf")

        for c in chain:
            strike = c.get("strike")
            iv = c.get("implied_volatility")
            if not strike or not iv:
                continue

            diff = abs(strike - underlying_price)
            if diff < min_diff:
                min_diff = diff
                closest = iv

        return closest

    # ---------------------------------------------------------
    # Utility: compute skew (25-delta RR)
    # ---------------------------------------------------------
    def _skew(self, chain, underlying_price):
        calls = []
        puts = []

        for c in chain:
            strike = c.get("strike")
            iv = c.get("implied_volatility")
            if not strike or not iv:
                continue

            if strike > underlying_price:
                calls.append(iv)
            else:
                puts.append(iv)

        if not calls or not puts:
            return None

        call_iv = sum(calls) / len(calls)
        put_iv = sum(puts) / len(puts)

        return call_iv - put_iv

    # ---------------------------------------------------------
    # Utility: term structure (near vs next expiry)
    # ---------------------------------------------------------
    def _term_structure(self, expiries):
        if len(expiries) < 2:
            return None

        sorted_exp = sorted(expiries.items(), key=lambda x: x[0])
        near_iv = sorted_exp[0][1]
        next_iv = sorted_exp[1][1]

        return {
            "near_expiry_iv": near_iv,
            "next_expiry_iv": next_iv,
            "slope": next_iv - near_iv,
        }

    # ---------------------------------------------------------
    # Main run()
    # ---------------------------------------------------------
    def run(self, ticker: str, expiry: str = None):
        url = EODHD_API.format(ticker=ticker, token=self.api_token)
        resp = requests.get(url)

        if resp.status_code != 200:
            return {"ok": False, "error": f"HTTP {resp.status_code} from EODHD"}

        data = resp.json()
        if not isinstance(data, dict) or "data" not in data:
            return {"ok": False, "error": f"Malformed response for {ticker}"}

        chain = data["data"]

        # Underlying price (EODHD includes it)
        underlying_price = data.get("underlying_price")

        # Group by expiry
        expiries = {}
        for c in chain:
            exp = c.get("expiration_date")
            iv = c.get("implied_volatility")
            if exp and iv:
                expiries.setdefault(exp, []).append(iv)

        expiry_iv = {
            exp: sum(ivs) / len(ivs)
            for exp, ivs in expiries.items()
            if ivs
        }

        # ATM IV
        atm_iv = self._atm_iv(chain, underlying_price)

        # Implied moves
        one_day_move = self._implied_move(atm_iv, 1)
        one_week_move = self._implied_move(atm_iv, 5)

        # Skew
        skew = self._skew(chain, underlying_price)

        # Term structure
        term = self._term_structure(expiry_iv)

        # IV surface (strike → IV)
        iv_surface = [
            {"strike": c.get("strike"), "iv": c.get("implied_volatility")}
            for c in chain
            if c.get("strike") and c.get("implied_volatility")
        ]

        return {
            "ok": True,
            "ticker": ticker,
            "underlying_price": underlying_price,
            "atm_iv": atm_iv,
            "implied_move_1d": one_day_move,
            "implied_move_1w": one_week_move,
            "skew_25d_rr": skew,
            "term_structure": term,
            "iv_surface": iv_surface,
            "raw_chain": chain,
        }
