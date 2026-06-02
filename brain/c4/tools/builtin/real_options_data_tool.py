# brain/c4/tools/builtin/real_options_data_tool.py

from typing import Any, Dict

from brain.c4.tools.base import Tool
from brain.c4.tools.builtin.options_data_tool import OptionsDataTool
from brain.c4.tools.builtin.options_cache import OptionsDataCache

from brain.c4.tools.builtin.yfinance_client import YFinanceOptionsClient
from brain.c4.tools.builtin.yfinance_normalizer import YFinanceOptionsNormalizer


class RealOptionsDataTool(Tool):
    """
    C2: Real Options Chain + IV Metrics + Greeks (yfinance-backed, B2-compatible schema)
    """

    def __init__(
        self,
        cache: OptionsDataCache | None = None,
        fallback_tool: OptionsDataTool | None = None,
    ):
        super().__init__(
            name="real_options_data",
            description="Fetches real options chain, IV metrics, and Greeks for a ticker (yfinance-backed, B2 schema).",
        )

        self._cache = cache or OptionsDataCache()
        self._fallback = fallback_tool or OptionsDataTool()

        self._yf = YFinanceOptionsClient()
        self._yf_norm = YFinanceOptionsNormalizer()

    def run(self, **kwargs) -> Dict[str, Any]:
        ticker = kwargs.get("ticker")
        if not ticker:
            return {"error": "ticker missing"}

        cache_key = ("snapshot", ticker)

        cached = self._cache.get(cache_key)
        if cached is not None:
            return self._with_source(cached, source="real_cached")

        ok, data = self._yf.get_chain(ticker)
        if ok:
            try:
                normalized = self._yf_norm.normalize(ticker, data)
                if normalized:
                    self._cache.set(cache_key, normalized)
                    return self._with_source(normalized, source="real_yfinance")
            except Exception:
                pass

        return self._fallback_with_source(ticker, reason="yfinance_error")

    def _fallback_with_source(self, ticker: str, reason: str) -> Dict[str, Any]:
        base = self._fallback.run(ticker=ticker)
        return self._with_source(base, source=f"synthetic_fallback:{reason}")

    @staticmethod
    def _with_source(payload: Dict[str, Any], source: str) -> Dict[str, Any]:
        out = dict(payload)
        out["source"] = source
        return out

