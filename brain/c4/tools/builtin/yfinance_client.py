# brain/c4/tools/builtin/yfinance_client.py

import yfinance as yf
from typing import Any, Dict, Tuple, List


class YFinanceOptionsClient:
    """
    Thin wrapper around yfinance for fetching full options chains.
    """

    def get_chain(self, ticker: str) -> Tuple[bool, Any]:
        """
        Returns (ok, raw_data_or_error)
        raw_data format:
        {
            "ticker": str,
            "expirations": [...],
            "chains": {
                "2024-06-21": {
                    "calls": [...],
                    "puts": [...]
                },
                ...
            }
        }
        """
        try:
            tk = yf.Ticker(ticker)
            expirations = tk.options
            if not expirations:
                return False, {"error": "no_expirations"}

            chains: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

            for exp in expirations:
                try:
                    opt = tk.option_chain(exp)
                except Exception:
                    continue

                calls = opt.calls.to_dict("records") if hasattr(opt, "calls") else []
                puts = opt.puts.to_dict("records") if hasattr(opt, "puts") else []

                chains[exp] = {
                    "calls": calls or [],
                    "puts": puts or [],
                }

            if not chains:
                return False, {"error": "empty_chain"}

            return True, {
                "ticker": ticker,
                "expirations": expirations,
                "chains": chains,
            }

        except Exception:
            return False, {"error": "request_failed"}
