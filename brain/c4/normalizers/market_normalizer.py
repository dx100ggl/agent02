# brain/c4/normalizers/market_normalizer.py

from __future__ import annotations
from typing import Any, Dict
from .normalizer_base import Normalizer


class MarketDataNormalizer(Normalizer):
    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            return {}

        return {
            "trend": raw.get("trend") or raw.get("summary") or "n/a",
            "volatility": raw.get("volatility") or "n/a",
            "levels": {
                "support": raw.get("support"),
                "resistance": raw.get("resistance"),
            },
            "recent_moves": raw.get("recent_moves") or raw.get("price_action"),
        }
