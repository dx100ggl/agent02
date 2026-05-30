# brain/c2/skill_learning/research_skill.py

from __future__ import annotations
from typing import Dict, Any


class ResearchSkill:
    """
    Aggregates outputs from the research tools into a unified structure
    that the Synthesizer can turn into a research brief.
    """

    name = "equity_research_skill"

    def run(self, plan_result: Dict[str, Any], state) -> Dict[str, Any]:
        sections = {
            "technical": plan_result.get("fetch_market_data", {}),
            "options": plan_result.get("fetch_options_data", {}),
            "sentiment": plan_result.get("fetch_sentiment_data", {}),
            "macro": plan_result.get("fetch_macro_overlay", {}),
            "analogs": plan_result.get("search_historical_analogs", {}),
        }

        state.meta["research_sections"] = sections
        state.meta["ticker"] = plan_result.get("fetch_market_data", {}).get("ticker", "UNKNOWN")

        return sections
