# brain/c4/normalizers/analogs_normalizer.py

from __future__ import annotations
from typing import Any, Dict
from .normalizer_base import Normalizer


class AnalogsNormalizer(Normalizer):
    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            return {}

        return {
            "closest_match": raw.get("closest_match") or "n/a",
            "pattern_summary": raw.get("pattern_summary") or raw.get("summary"),
            "similarity_score": raw.get("similarity_score"),
        }
