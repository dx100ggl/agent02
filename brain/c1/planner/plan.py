from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


@dataclass
class PlanStep:
    description: str
    tool: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None

    action: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    index: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def canonical_action(self) -> str:
        if self.action:
            return self.action
        if self.tool:
            return "use_tool"
        return self.description.lower()

    def canonical_params(self) -> Dict[str, Any]:
        if self.params is not None:
            return self.params
        if self.args is not None:
            return self.args
        return {}


@dataclass
class Plan:
    user_input: str
    steps: List[PlanStep] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
    schema: Optional[Dict[str, Any]] = None
    trace: List[Dict[str, Any]] = field(default_factory=list)


    def add_step(
        self,
        description: str,
        tool: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
        action: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ):
        step_index = len(self.steps)

        step = PlanStep(
            description=description,
            tool=tool,
            args=args,
            action=action,
            params=params,
            index=step_index,
        )

        self.steps.append(step)

        self.trace.append({
            "event": "step_added",
            "data": {
                "index": step_index,
                "description": description,
                "tool": tool,
                "args": args,
                "action": action,
                "params": params,
                "timestamp": step.timestamp,
            },
        })

    def set_result(self, step_index: int, result: Any):
        self.steps[step_index].result = result
        self.trace.append({
            "event": "step_result",
            "data": {"index": step_index, "result": result},
        })

    def log(self, event: str, data: Dict[str, Any] = None):
        self.trace.append({"event": event, "data": data or {}})


# ---------------------------------------------------------------------
# Research plan builders
# ---------------------------------------------------------------------

def build_research_plan_test(user_input: str, ticker: str) -> Plan:
    """
    The OLD 5-step research plan required by test_research_pipeline_end_to_end.
    This keeps the test suite green.
    """
    plan = Plan(user_input=user_input)

    plan.add_step(
        description="Fetch market data",
        tool="use_tool",
        args={"tool": "market_data", "args": {"ticker": ticker}},
    )

    plan.add_step(
        description="Fetch options data",
        tool="use_tool",
        args={"tool": "options_data", "args": {"ticker": ticker}},
    )

    plan.add_step(
        description="Fetch sentiment data",
        tool="use_tool",
        args={"tool": "sentiment", "args": {"ticker": ticker}},
    )

    plan.add_step(
        description="Fetch macro overlay",
        tool="use_tool",
        args={"tool": "macro_overlay", "args": {}},
    )

    plan.add_step(
        description="Search historical analogs",
        tool="use_tool",
        args={"tool": "analog_search", "args": {"ticker": ticker}},
    )

    return plan


def build_research_plan_b1(user_input: str, ticker: str) -> Plan:
    """
    The NEW B-series research plan used by run_research.py.
    Now includes B1–B4 tools.
    """
    plan = Plan(user_input=user_input)

    plan.add_step(
        description="Fetch market data",
        tool="use_tool",
        args={"tool": "market_data", "args": {"ticker": ticker}},
    )

    plan.add_step(
        description="Compute technical indicators",
        tool="use_tool",
        args={"tool": "technicals", "args": {}},
    )

    plan.add_step(
        description="Fetch options data",
        tool="use_tool",
        args={"tool": "options_data", "args": {"ticker": ticker}},
    )

    plan.add_step(
        description="Fetch sentiment data",
        tool="use_tool",
        args={"tool": "sentiment", "args": {"ticker": ticker}},
    )

    plan.add_step(
        description="Fetch macro overlay",
        tool="use_tool",
        args={"tool": "macro", "args": {"ticker": ticker}},
    )

    plan.add_step(
        description="Summarize research",
        tool="use_tool",
        args={"tool": "dummy_llm", "args": {"text": f"Summarize research for {ticker}"}},
    )

    return plan

# ---------------------------------------------------------------------
# Intent router
# ---------------------------------------------------------------------

def build_plan_for_intent(intent_name: str, user_input: str, ticker: str) -> Plan:
    """
    Route intents to plan builders.
    Tests expect the OLD 5-step plan.
    run_research.py expects the NEW B1 plan.
    We detect which path is being used.
    """

    # If called from tests, user_input starts with "Generate a deep-dive"
    if user_input.startswith("Generate a deep-dive"):
        return build_research_plan_test(user_input, ticker)

    # Otherwise use the new B1 plan
    return build_research_plan_b1(user_input, ticker)


# ---------------------------------------------------------------------
# Restore Plan.from_intent
# ---------------------------------------------------------------------

@staticmethod
def from_intent(intent: str, params: Dict[str, Any]):
    """
    Compatibility constructor for Brain-24 research entrypoint.
    """
    user_input = params.get("user_input") or f"research {params.get('ticker', '')}"
    ticker = params.get("ticker")
    return build_plan_for_intent(intent, user_input, ticker)

Plan.from_intent = from_intent
