# brain/c4/tools/builtin/analogs_tool.py

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

from brain.c4.tools.base import Tool


class AnalogsTool(Tool):
    """
    Deterministic synthetic historical analog search.

    For now this is NOT real market data – it returns a stable,
    hard-coded set of "analogs" keyed off the ticker, horizon, etc.
    """

    def __init__(self):
        super().__init__(
            name="analogs",
            description="Return synthetic historical analog patterns for a given ticker.",
        )

    def _now(self) -> datetime:
        # Single point of time control for determinism / testing
        return datetime.now(timezone.utc)

    def _build_analog(
        self,
        base_ticker: str,
        analog_ticker: str,
        offset_days: int,
        similarity: float,
        regime: str,
        notes: str,
    ) -> Dict[str, Any]:
        end = self._now() - timedelta(days=offset_days)
        start = end - timedelta(days=90)

        return {
            "ticker": analog_ticker,
            "base_ticker": base_ticker,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "similarity": round(similarity, 3),
            "regime": regime,
            "notes": notes,
        }

    def run(
        self,
        ticker: str,
        horizon: str = "swing",
        depth: str = "deep",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Return a small set of deterministic analogs for the given ticker.
        Accept **kwargs because the executor merges all prior tool outputs.
        """

        n = len(ticker.upper())

        analogs: List[Dict[str, Any]] = []

        analogs.append(
            self._build_analog(
                base_ticker=ticker,
                analog_ticker="NVDA" if n % 2 == 0 else "AMD",
                offset_days=365,
                similarity=0.83,
                regime="post-breakout consolidation",
                notes=f"{ticker} currently resembles a prior {('NVDA' if n % 2 == 0 else 'AMD')} regime "
                    f"with elevated volatility and trend persistence.",
            )
        )

        analogs.append(
            self._build_analog(
                base_ticker=ticker,
                analog_ticker="SMH",
                offset_days=540,
                similarity=0.78,
                regime="sector rotation",
                notes=f"Pattern suggests {ticker} trading in line with a prior semiconductor ETF rotation phase.",
            )
        )

        analogs.append(
            self._build_analog(
                base_ticker=ticker,
                analog_ticker="QQQ",
                offset_days=720,
                similarity=0.74,
                regime="macro-driven pullback",
                notes=f"Macro sensitivity for {ticker} is similar to a prior QQQ correction-and-recovery cycle.",
            )
        )

        return {
            "ticker": ticker,
            "horizon": horizon,
            "depth": depth,
            "analogs": analogs,
        }
