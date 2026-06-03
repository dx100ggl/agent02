# brain/c4/normalizers/sentiment_normalizer.py

from __future__ import annotations
from typing import Any, Dict
from .normalizer_base import Normalizer


class SentimentNormalizer(Normalizer):
    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            return {}

        return {
            "news_sentiment": raw.get("news") or "n/a",
            "social_sentiment": raw.get("social") or "n/a",
            "fear_greed": raw.get("fear_greed") or "n/a",
            "narrative": raw.get("narrative") or raw.get("summary"),
        }
