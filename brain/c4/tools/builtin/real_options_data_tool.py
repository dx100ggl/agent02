# brain/c4/tools/builtin/real_options_data_tool.py

from typing import Any, Dict

from brain.c4.tools.base import Tool
from brain.c4.tools.builtin.options_data_tool import OptionsDataTool
from brain.c4.tools.builtin.options_cache import OptionsDataCache

from brain.c4.tools.builtin.yahoo_client import YahooOptionsClient
from brain.c4.tools.builtin.yahoo_normalizer import YahooOptionsNormalizer


class RealOptionsDataTool(Tool):
    """
    C2: Real Options Chain + IV Metrics + Greeks (Yahoo-backed, B2-compatible schema)

    Behaviour:
    - Attempts to fetch real options chain data from Yahoo Finance.
    - Normalizes into the exact B2 schema.
    - Uses a small TTL cache to avoid hammering the API.
    - On any failure (network, schema, missing fields), falls back
      to the deterministic B2 OptionsDataTool.
    """

    def __init__(
        self,
        cache: OptionsDataCache | None = None,
        fallback_tool: OptionsDataTool | None = None,
    ):
        super().__init__(
            name="real_options_data",
            description="Fetches real options chain, IV metrics, and Greeks for a ticker (Yahoo-backed, B2 schema).",
        )

        self._cache = cache or OptionsDataCache()
        self._fallback = fallback_tool or OptionsDataTool()

        # Yahoo provider
        self._yahoo = YahooOptionsClient()
        self._yahoo_norm = YahooOptionsNormalizer()

    # ------------------------------------------------------------------ #
    # Public Tool API
    # ------------------------------------------------------------------ #

    def run(self, **kwargs) -> Dict[str, Any]:
        ticker = kwargs.get("ticker")
        if not ticker:
            return {"error": "ticker missing"}

        cache_key = ("snapshot", ticker)

        # 1. Cache hit
        cached = self._cache.get(cache_key)
        if cached is not None:
            return self._with_source(cached, source="real_cached")

        # 2. Try Yahoo Finance (free)
        ok, data = self._yahoo.get_chain(ticker)
        if ok:
            try:
                normalized = self._yahoo_norm.normalize(ticker, data)
                if normalized:
                    self._cache.set(cache_key, normalized)
                    return self._with_source(normalized, source="real_yahoo")
            except Exception:
                pass  # fall through to fallback

        # 3. Fallback to deterministic B2 tool
        return self._fallback_with_source(ticker, reason="yahoo_error")

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _fallback_with_source(self, ticker: str, reason: str) -> Dict[str, Any]:
        base = self._fallback.run(ticker=ticker)
        return self._with_source(base, source=f"synthetic_fallback:{reason}")

    @staticmethod
    def _with_source(payload: Dict[str, Any], source: str) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            return payload
        out = dict(payload)
        out["source"] = source
        return out
