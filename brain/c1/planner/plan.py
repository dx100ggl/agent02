# brain/c1/planner/plan.py

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from brain.c4.tools.builtin.fundamentals_tool import FUNDAMENTALS_TOOL_NAME


# ---------------------------------------------------------------------------
# Step Kinds
# ---------------------------------------------------------------------------

class PlanStepKind(str, Enum):
    SEARCH = "search"
    TOOL = "tool"
    SYNTHESIZE = "synthesize"
    FUNDAMENTALS = "fundamentals"   # <-- NEW


# ---------------------------------------------------------------------------
# Plan Step + Plan
# ---------------------------------------------------------------------------

@dataclass
class PlanStep:
    kind: PlanStepKind
    tool_name: Optional[str]
    params: Dict[str, Any]


@dataclass
class ResearchPlan:
    steps: List[PlanStep]

class PlanStepKind(str, Enum):
    SEARCH = "search"
    TOOL = "tool"
    SYNTHESIZE = "synthesize"
    FUNDAMENTALS = "fundamentals"
    MARKET_DATA = "market_data"
    TECHNICALS = "technicals_data"
    OPTIONS = "options_data"
    SENTIMENT = "sentiment_data"
    MACRO = "macro_data"
    ANALOGS = "analogs_data"


# ---------------------------------------------------------------------------
# Fundamentals‑aware plan builder
# ---------------------------------------------------------------------------

def build_fundamentals_plan(
    ticker: str,
    intent: str,
    as_of: Optional[str] = None,
) -> ResearchPlan:
    """
    Minimal C1 plan builder for fundamentals → synthesis.
    C2 executor + C4 synthesizer will consume this.
    """
    steps: List[PlanStep] = []

    # Step 1: Fundamentals tool
    steps.append(
        PlanStep(
            kind=PlanStepKind.FUNDAMENTALS,
            tool_name=FUNDAMENTALS_TOOL_NAME,
            params={
                "ticker": ticker,
                "as_of": as_of,
            },
        )
    )

    # Step 2: Synthesis
    steps.append(
        PlanStep(
            kind=PlanStepKind.SYNTHESIZE,
            tool_name=None,
            params={
                "ticker": ticker,
                "intent": intent,
            },
        )
    )

    return ResearchPlan(steps=steps)

def build_full_research_plan(
    ticker: str,
    intent: str,
    as_of: Optional[str] = None,
) -> ResearchPlan:
    """
    Multi‑tool research plan:
    1. Market data
    2. Technicals
    3. Options chain
    4. Sentiment
    5. Macro
    6. Analogs
    7. Fundamentals
    8. Synthesis
    """
    steps: List[PlanStep] = []

    # 1. Market data
    steps.append(
        PlanStep(
            kind=PlanStepKind.MARKET_DATA,
            tool_name="market_data",
            params={"ticker": ticker},
        )
    )

    # 2. Technicals
    steps.append(
        PlanStep(
            kind=PlanStepKind.TECHNICALS,
            tool_name="technicals_data",
            params={"ticker": ticker},
        )
    )

    # 3. Options chain
    steps.append(
        PlanStep(
            kind=PlanStepKind.OPTIONS,
            tool_name="options_data",
            params={"ticker": ticker},
        )
    )

    # 4. Sentiment
    steps.append(
        PlanStep(
            kind=PlanStepKind.SENTIMENT,
            tool_name="sentiment_data",
            params={"ticker": ticker},
        )
    )

    # 5. Macro
    steps.append(
        PlanStep(
            kind=PlanStepKind.MACRO,
            tool_name="macro_data",
            params={"ticker": ticker},
        )
    )

    # 6. Analogs
    steps.append(
        PlanStep(
            kind=PlanStepKind.ANALOGS,
            tool_name="analogs_data",
            params={"ticker": ticker},
        )
    )

    # 7. Fundamentals
    steps.append(
        PlanStep(
            kind=PlanStepKind.FUNDAMENTALS,
            tool_name="fundamentals_data",
            params={"ticker": ticker, "as_of": as_of},
        )
    )

    # 8. Synthesis
    steps.append(
        PlanStep(
            kind=PlanStepKind.SYNTHESIZE,
            tool_name=None,
            params={"ticker": ticker, "intent": intent},
        )
    )

    return ResearchPlan(steps=steps)
