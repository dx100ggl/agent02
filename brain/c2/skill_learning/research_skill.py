from __future__ import annotations
from typing import Dict, Any


class ResearchSkill:
    """
    Aggregates outputs from the research tools into a unified structure
    that the Synthesizer can turn into a research brief.
    """

    name = "equity_research_skill"

    CANONICAL_MAP = {
        "fetch_market_data": "technical",
        "fetch_options_data": "options",
        "fetch_sentiment_data": "sentiment",
        "fetch_macro_overlay": "macro",
        "search_historical_analogs": "analogs",
    }

    def run(self, plan_result: Dict[str, Any], state) -> Dict[str, Any]:

        sections = {}

        # ---------------------------------------------------------
        # SAFE TICKER EXTRACTION (works for FakeState + BrainState)
        # ---------------------------------------------------------
        context = getattr(state, "context", {}) or {}
        meta = getattr(state, "meta", {}) or {}

        ticker = (
            context.get("ticker")
            or meta.get("ticker")
            or self._extract_ticker_from_user_input(state.user_input)
        )

        # Store ticker for synthesizer
        state.meta["ticker"] = ticker

        # ---------------------------------------------------------
        # MAP TOOL OUTPUTS INTO CANONICAL SECTIONS
        # ---------------------------------------------------------
        for step_key, section_name in self.CANONICAL_MAP.items():
            sections[section_name] = plan_result.get(step_key, {})

        # ---------------------------------------------------------
        # STORE SECTIONS FOR SYNTHESIZER
        # ---------------------------------------------------------
        state.meta["research_sections"] = sections

        return sections

    # -------------------------------------------------------------
    # FALLBACK TICKER EXTRACTION
    # -------------------------------------------------------------
    def _extract_ticker_from_user_input(self, text: str) -> str:
        # Very simple fallback: last token, uppercased
        return text.strip().split()[-1].upper()
