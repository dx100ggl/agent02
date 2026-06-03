# brain/c4/normalizers/technicals_normalizer.py

from __future__ import annotations
from typing import Any, Dict
from .normalizer_base import Normalizer


class TechnicalsNormalizer(Normalizer):
    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            return {}

        return {
            "momentum": raw.get("momentum") or "n/a",
            "trend": raw.get("trend") or "n/a",
            "support": raw.get("support"),
            "resistance": raw.get("resistance"),
            "signals": raw.get("signals") or [],
        }
