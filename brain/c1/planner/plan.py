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
# UPDATED: canonical tool names matching ToolRegistry
# ---------------------------------------------------------------------
def build_research_plan(user_input: str, ticker: str) -> Plan:
    """
    Build a tool-based research plan for an equity ticker.
    Steps are aligned with Executor's 'use_tool' convention.
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


def build_plan_for_intent(intent_name: str, user_input: str, ticker: str) -> Plan:
    if intent_name == "equity_research":
        return build_research_plan(user_input, ticker)

    return Plan(user_input=user_input)
