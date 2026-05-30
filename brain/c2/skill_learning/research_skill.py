# brain/c2/skill_learning/research_skill.py

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

        for step_key, section_name in self.CANONICAL_MAP.items():
            sections[section_name] = plan_result.get(step_key, {})

        # Store in state.meta for Synthesizer
        state.meta["research_sections"] = sections

        # Extract ticker if available
        tech = sections.get("technical", {})
        state.meta["ticker"] = tech.get("ticker", "UNKNOWN")

        return sections
