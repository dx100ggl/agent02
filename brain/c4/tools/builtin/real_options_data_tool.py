from typing import Any, Dict

from brain.c4.tools.base import Tool
from brain.c4.tools.builtin.options_data_tool import OptionsDataTool
from brain.c4.tools.builtin.options_normalizer import OptionsChainNormalizer
from brain.c4.tools.builtin.options_cache import OptionsDataCache
from brain.c4.tools.builtin.polygon_client import PolygonOptionsClient


class RealOptionsDataTool(Tool):
    """
    C2: Real Options Chain + IV Metrics + Greeks (Polygon-backed, B2-compatible schema)

    Behaviour:
    - Attempts to fetch real options snapshot from Polygon.
    - Normalizes into the exact B2 schema.
    - Uses a small TTL cache to avoid hammering the API.
    - On any failure (network, rate-limit, schema, missing API key), falls back
      to the deterministic B2 OptionsDataTool.
    """

    def __init__(
        self,
        polygon_client: PolygonOptionsClient | None = None,
        cache: OptionsDataCache | None = None,
        fallback_tool: OptionsDataTool | None = None,
    ):
        super().__init__(
            name="real_options_data",
            description="Fetches real options chain, IV metrics, and Greeks for a ticker (Polygon-backed, B2 schema).",
        )
        self._client = polygon_client or PolygonOptionsClient()
        self._cache = cache or OptionsDataCache()
        self._normalizer = OptionsChainNormalizer()
        self._fallback = fallback_tool or OptionsDataTool()

    # ------------------------------------------------------------------ #
    # Public Tool API
    # ------------------------------------------------------------------ #

    def run(self, **kwargs) -> Dict[str, Any]:
        ticker = kwargs.get("ticker")
        if not ticker:
            return {"error": "ticker missing"}

        # Cache key: just ticker for now (you can extend with filters later)
        cache_key = ("snapshot", ticker)

        cached = self._cache.get(cache_key)
        if cached is not None:
            # cached is already in B2 schema
            return self._with_source(cached, source="real_cached")

        # Try real data path
        ok, data = self._client.get_snapshot_chain(ticker)
        if not ok:
            # Any client-level failure → fallback
            return self._fallback_with_source(ticker, reason=data.get("error", "client_error"))

        try:
            normalized = self._normalizer.normalize(ticker, data)
        except Exception:
            # Normalization failure → fallback
            return self._fallback_with_source(ticker, reason="normalization_error")

        # If chain is empty, you may choose to fallback or not.
        # Here we treat empty real chain as "real but empty" (no fallback).
        self._cache.set(cache_key, normalized)
        return self._with_source(normalized, source="real")

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _fallback_with_source(self, ticker: str, reason: str) -> Dict[str, Any]:
        """
        Call deterministic B2 OptionsDataTool and annotate source.
        """
        base = self._fallback.run(ticker=ticker)
        return self._with_source(base, source=f"synthetic_fallback:{reason}")

    @staticmethod
    def _with_source(payload: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Non-breaking metadata: attach a 'source' field at top level.
        Existing tests that don't look at 'source' remain green.
        """
        if not isinstance(payload, dict):
            return payload
        # Do not mutate original dict in case caller reuses it
        out = dict(payload)
        out["source"] = source
        return out
