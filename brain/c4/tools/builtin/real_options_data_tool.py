# brain/c4/tools/builtin/real_options_data_tool.py

from typing import Any, Dict

from brain.c4.tools.base import Tool
from brain.c4.tools.builtin.options_data_tool import OptionsDataTool
from brain.c4.tools.builtin.options_cache import OptionsDataCache

from brain.c4.tools.builtin.eodhd_client import EODHDOptionsClient
from brain.c4.tools.builtin.eodhd_normalizer import EODHDOptionsNormalizer


class RealOptionsDataTool(Tool):
    """
    C2: Real Options Chain + IV Metrics + Greeks (EODHD-backed, B2-compatible schema)

    Behaviour:
    - Attempts to fetch real options chain data from EODHD.
    - Normalizes into the exact B2 schema.
    - Uses a small TTL cache to avoid hammering the API.
    - On any failure (network, schema, provider error), falls back
      to the deterministic B2 OptionsDataTool.
    """

    def __init__(
        self,
        cache: OptionsDataCache | None = None,
        fallback_tool: OptionsDataTool | None = None,
    ):
        super().__init__(
            name="real_options_data",
            description="Fetches real options chain, IV metrics, and Greeks for a ticker (EODHD-backed, B2 schema).",
        )

        self._cache = cache or OptionsDataCache()
        self._fallback = fallback_tool or OptionsDataTool()

        self._eodhd = EODHDOptionsClient()
        self._eodhd_norm = EODHDOptionsNormalizer()

    # ------------------------------------------------------------------ #
    # Public Tool API
    # ------------------------------------------------------------------ #

    def run(self, **kwargs) -> Dict[str, Any]:
        ticker = kwargs.get("ticker")
        if not ticker:
            return {"error": "ticker missing"}

        cache_key = ("snapshot", ticker)

        # 1. Cache
        cached = self._cache.get(cache_key)
        if cached is not None:
            return self._with_source(cached, source="real_cached")

        # 2. Try EODHD
        ok, data = self._eodhd.get_chain(ticker)
        if ok:
            try:
                normalized = self._eodhd_norm.normalize(ticker, data)
                if normalized:
                    self._cache.set(cache_key, normalized)
                    return self._with_source(normalized, source="real_eodhd")
            except Exception:
                # fall through to fallback
                pass

        # 3. Fallback to deterministic B2
        return self._fallback_with_source(ticker, reason="eodhd_error")

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
