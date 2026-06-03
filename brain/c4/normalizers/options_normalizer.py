# brain/c4/normalizers/options_normalizer.py

from __future__ import annotations
from typing import Any, Dict
from .normalizer_base import Normalizer


class OptionsNormalizer(Normalizer):
    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            return {}

        return {
            "iv_rank": raw.get("iv_rank") or raw.get("ivr") or "n/a",
            "skew": raw.get("skew") or "n/a",
            "flow_summary": raw.get("flow_summary") or raw.get("flow") or "n/a",
            "volume": raw.get("volume"),
            "open_interest": raw.get("open_interest"),
        }
