# brain/c4/normalizers/macro_normalizer.py

from __future__ import annotations
from typing import Any, Dict
from .normalizer_base import Normalizer


class MacroNormalizer(Normalizer):
    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            return {}

        return {
            "rates": raw.get("rates") or "n/a",
            "inflation": raw.get("inflation") or "n/a",
            "growth": raw.get("growth") or "n/a",
            "macro_regime": raw.get("regime") or raw.get("summary"),
        }
