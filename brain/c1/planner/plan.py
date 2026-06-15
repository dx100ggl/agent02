# brain/c1/planner/plan.py

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from brain.c4.tools.builtin.fundamentals_tool import FUNDAMENTALS_TOOL_NAME


# ---------------------------------------------------------------------------
# Step Kinds (single unified enum)
# ---------------------------------------------------------------------------

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
# Plan Step (with backward‑compatible fields)
# ---------------------------------------------------------------------------

@dataclass
class PlanStep:
    kind: PlanStepKind
    tool_name: Optional[str]
    params: Dict[str, Any]

    # Legacy compatibility fields
    description: str = ""
    tool: Optional[str] = None

    def __post_init__(self):
        # Old planners expect step.tool
        if self.tool is None:
            self.tool = self.tool_name

        # Old planners expect step.description to be meaningful
        if not self.description:
            if self.tool_name:
                self.description = f"{self.kind.value}: {self.tool_name}"
            else:
                self.description = self.kind.value


# ---------------------------------------------------------------------------
# Research Plan (modern plan with legacy API)
# ---------------------------------------------------------------------------

@dataclass
class ResearchPlan:
    steps: List[PlanStep]
    meta: Dict[str, Any] = None

    def __post_init__(self):
        if self.meta is None:
            self.meta = {}

        # Ensure belief slot exists (C5 → C2 → C1 integration)
        if "beliefs" not in self.meta:
            self.meta["beliefs"] = []

    # ------------------------------------------------------------------
    # Belief integration (C5 → C1)
    # ------------------------------------------------------------------
    def attach_beliefs(self, beliefs: List[Any]):
        """
        Attach C5 beliefs to the plan metadata.
        Non‑breaking: planners/tests that ignore beliefs continue to work.
        """
        self.meta["beliefs"] = beliefs or []

    # ------------------------------------------------------------------
    # Legacy API used by AdaptivePlanner
    # ------------------------------------------------------------------
    def add_step(self, description: str, tool: str, args: Dict[str, Any]):
        step = PlanStep(
            kind=PlanStepKind.TOOL if tool != "llm" else PlanStepKind.SYNTHESIZE,
            tool_name=tool,
            params=args,
            description=description,
            tool=tool,
        )
        self.steps.append(step)


# ---------------------------------------------------------------------------
# Fundamentals‑only plan
# ---------------------------------------------------------------------------

def build_fundamentals_plan(
    ticker: str,
    intent: str,
    as_of: Optional[str] = None,
) -> ResearchPlan:

    steps: List[PlanStep] = []

    steps.append(
        PlanStep(
            kind=PlanStepKind.FUNDAMENTALS,
            tool_name=FUNDAMENTALS_TOOL_NAME,
            params={"ticker": ticker, "as_of": as_of},
            description="Fetch fundamentals",
        )
    )

    steps.append(
        PlanStep(
            kind=PlanStepKind.SYNTHESIZE,
            tool_name=None,
            params={"ticker": ticker, "intent": intent},
            description="Synthesize fundamentals",
        )
    )

    return ResearchPlan(steps=steps)


# ---------------------------------------------------------------------------
# Full multi‑tool research plan
# ---------------------------------------------------------------------------

def build_full_research_plan(
    ticker: str,
    intent: str,
    as_of: Optional[str] = None,
) -> ResearchPlan:

    steps: List[PlanStep] = []

    steps.append(
        PlanStep(
            kind=PlanStepKind.MARKET_DATA,
            tool_name="market_data",
            params={"ticker": ticker},
            description="Fetch market data",
        )
    )

    steps.append(
        PlanStep(
            kind=PlanStepKind.TECHNICALS,
            tool_name="technicals_data",
            params={"ticker": ticker},
            description="Fetch technical indicators",
        )
    )

    steps.append(
        PlanStep(
            kind=PlanStepKind.OPTIONS,
            tool_name="options_data",
            params={"ticker": ticker},
            description="Fetch options chain",
        )
    )

    steps.append(
        PlanStep(
            kind=PlanStepKind.SENTIMENT,
            tool_name="sentiment_data",
            params={"ticker": ticker},
            description="Fetch sentiment data",
        )
    )

    steps.append(
        PlanStep(
            kind=PlanStepKind.MACRO,
            tool_name="macro_data",
            params={"ticker": ticker},
            description="Fetch macro indicators",
        )
    )

    steps.append(
        PlanStep(
            kind=PlanStepKind.ANALOGS,
            tool_name="analogs_data",
            params={"ticker": ticker},
            description="Search historical analogs",
        )
    )

    steps.append(
        PlanStep(
            kind=PlanStepKind.FUNDAMENTALS,
            tool_name="fundamentals_data",
            params={"ticker": ticker, "as_of": as_of},
            description="Fetch fundamentals",
        )
    )

    steps.append(
        PlanStep(
            kind=PlanStepKind.SYNTHESIZE,
            tool_name=None,
            params={"ticker": ticker, "intent": intent},
            description="Synthesize research",
        )
    )

    return ResearchPlan(steps=steps)


# ---------------------------------------------------------------------------
# Compatibility alias
# ---------------------------------------------------------------------------

Plan = ResearchPlan
