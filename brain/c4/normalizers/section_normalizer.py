# brain/c4/normalizers/section_normalizer.py
# This is the master normalizer.

from __future__ import annotations
from typing import Dict, Any

from .market_normalizer import MarketDataNormalizer
from .technicals_normalizer import TechnicalsNormalizer
from .options_normalizer import OptionsNormalizer
from .sentiment_normalizer import SentimentNormalizer
from .macro_normalizer import MacroNormalizer
from .analogs_normalizer import AnalogsNormalizer
from .fundamentals_normalizer import FundamentalsNormalizer


class SectionNormalizer:
    """
    Normalizes all tool outputs into a consistent schema.
    """

    def __init__(self):
        self.market = MarketDataNormalizer()
        self.technicals = TechnicalsNormalizer()
        self.options = OptionsNormalizer()
        self.sentiment = SentimentNormalizer()
        self.macro = MacroNormalizer()
        self.analogs = AnalogsNormalizer()
        self.fundamentals = FundamentalsNormalizer()

    def normalize(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "market": self.market.normalize(ctx.get("market_data")),
            "technicals": self.technicals.normalize(ctx.get("technicals_data")),
            "options": self.options.normalize(ctx.get("options_data")),
            "sentiment": self.sentiment.normalize(ctx.get("sentiment_data")),
            "macro": self.macro.normalize(ctx.get("macro_data")),
            "analogs": self.analogs.normalize(ctx.get("analogs_data")),
            "fundamentals": self.fundamentals.normalize(ctx.get("fundamentals_data")),
        }
