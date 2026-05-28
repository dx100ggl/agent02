# brain/c1/planner/plan.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


# =========================================================
# S4 PlanStep
# =========================================================
@dataclass
class PlanStep:
    """
    S4 PlanStep

    Backward‑compatible fields:
        - description
        - tool
        - args
        - result

    New S4 fields:
        - action: canonical verb for skill replay (e.g., "use_tool", "llm", "think")
        - params: canonical argument dict for skill replay
        - index: stable step index (set by Plan when added)
        - timestamp: creation time for trace alignment
    """

    description: str
    tool: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None

    # S4 additions
    action: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    index: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # -----------------------------------------------------
    # S4: canonicalize step for skill replay
    # -----------------------------------------------------
    def canonical_action(self) -> str:
        if self.action:
            return self.action
        if self.tool:
            return self.tool
        return self.description.lower()

    def canonical_params(self) -> Dict[str, Any]:
        if self.params is not None:
            return self.params
        if self.args is not None:
            return self.args
        return {}


# =========================================================
# S4 Plan
# =========================================================
@dataclass
class Plan:
    """
    Unified plan structure used across C1, C2, C4, C5, C7.

    S4 additions:
        - step indexing
        - richer trace events
        - stable metadata for reflection + skill learning
    """

    user_input: str
    steps: List[PlanStep] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
    schema: Optional[Dict[str, Any]] = None
    trace: List[Dict[str, Any]] = field(default_factory=list)

    # -----------------------------------------------------
    # Add a step (S4: assign index + canonical fields)
    # -----------------------------------------------------
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

        # S4 trace event
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

    # -----------------------------------------------------
    # Set result for a step
    # -----------------------------------------------------
    def set_result(self, step_index: int, result: Any):
        self.steps[step_index].result = result

        # S4 trace event
        self.trace.append({
            "event": "step_result",
            "data": {
                "index": step_index,
                "result": result,
            },
        })

    # -----------------------------------------------------
    # Generic trace logging
    # -----------------------------------------------------
    def log(self, event: str, data: Dict[str, Any] = None):
        self.trace.append({
            "event": event,
            "data": data or {},
        })
