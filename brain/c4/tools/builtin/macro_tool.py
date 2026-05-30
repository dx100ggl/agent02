from datetime import datetime
from brain.c4.tools.base import Tool


class MacroTool(Tool):
    """
    B4: Deterministic macro overlay for a ticker.
    Schema-first, no external data yet.
    """

    def __init__(self):
        super().__init__(
            name="macro",
            description="Provides deterministic macro context relevant to a ticker."
        )

    def run(self, **kwargs):
        ticker = kwargs.get("ticker")
        if not ticker:
            return {"error": "ticker missing"}

        now = datetime.utcnow().isoformat()

        # Deterministic macro snapshot
        rates = {
            "fed_funds_rate": 0.0525,
            "ten_year_yield": 0.043,
            "two_year_yield": 0.046,
            "timestamp": now,
        }

        inflation = {
            "cpi_yoy": 0.032,
            "core_cpi_yoy": 0.029,
            "ppi_yoy": 0.025,
            "timestamp": now,
        }

        growth = {
            "gdp_growth_qoq": 0.018,
            "gdp_growth_yoy": 0.021,
            "ism_manufacturing": 51.2,
            "ism_services": 52.8,
            "timestamp": now,
        }

        risk = {
            "vix": 17.5,
            "credit_spread_ig": 0.013,
            "credit_spread_hy": 0.042,
            "timestamp": now,
        }

        # Simple deterministic “relevance” tags
        relevance = {
            "rate_sensitive": True,
            "growth_sensitive": True,
            "inflation_sensitive": False,
            "commentary": (
                f"{ticker} is modeled as moderately sensitive to rates and growth, "
                "with limited direct inflation linkage in this deterministic stub."
            ),
        }

        return {
            "ticker": ticker,
            "rates": rates,
            "inflation": inflation,
            "growth": growth,
            "risk": risk,
            "relevance": relevance,
        }
