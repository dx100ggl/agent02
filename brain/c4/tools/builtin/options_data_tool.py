from datetime import datetime, timedelta, timezone
from brain.c4.tools.base import Tool


class OptionsDataTool(Tool):
    """
    B2: Deterministic Options Chain + IV Metrics + Greeks
    """

    def __init__(self):
        super().__init__(
            name="options_data",
            description="Fetches options chain, IV metrics, and Greeks for a ticker."
        )

    def run(self, **kwargs):
        ticker = kwargs.get("ticker")
        if not ticker:
            return {"error": "ticker missing"}

        today = datetime.now(timezone.utc)
        expirations = [
            today + timedelta(days=7),
            today + timedelta(days=30),
            today + timedelta(days=60),
        ]

        iv = 0.42
        iv_rank = 0.63
        iv_percentile = 0.58

        greeks = {
            "delta": 0.52,
            "gamma": 0.014,
            "theta": -0.62,
            "vega": 0.11,
        }

        chain = []
        for exp in expirations:
            chain.append({
                "expiration": exp.isoformat(),
                "calls": [
                    {
                        "strike": 100,
                        "bid": 5.10,
                        "ask": 5.40,
                        "iv": iv,
                        "delta": greeks["delta"],
                        "gamma": greeks["gamma"],
                        "theta": greeks["theta"],
                        "vega": greeks["vega"],
                    },
                    {
                        "strike": 110,
                        "bid": 2.80,
                        "ask": 3.10,
                        "iv": iv,
                        "delta": greeks["delta"] - 0.1,
                        "gamma": greeks["gamma"],
                        "theta": greeks["theta"],
                        "vega": greeks["vega"],
                    },
                ],
                "puts": [
                    {
                        "strike": 100,
                        "bid": 4.90,
                        "ask": 5.20,
                        "iv": iv,
                        "delta": -(greeks["delta"]),
                        "gamma": greeks["gamma"],
                        "theta": greeks["theta"],
                        "vega": greeks["vega"],
                    },
                    {
                        "strike": 90,
                        "bid": 2.40,
                        "ask": 2.70,
                        "iv": iv,
                        "delta": -(greeks["delta"] - 0.1),
                        "gamma": greeks["gamma"],
                        "theta": greeks["theta"],
                        "vega": greeks["vega"],
                    },
                ],
            })

        return {
            "ticker": ticker,
            "iv": iv,
            "iv_rank": iv_rank,
            "iv_percentile": iv_percentile,
            "greeks": greeks,
            "chain": chain,
        }
