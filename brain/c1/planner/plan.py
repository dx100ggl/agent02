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
