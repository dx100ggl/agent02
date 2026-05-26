from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class PlanStep:
    """A single step in a plan."""
    description: str
    tool: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None


@dataclass
class Plan:
    """Unified plan structure used across C1, C2, C4, C5."""
    user_input: str
    steps: List[PlanStep] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
    schema: Optional[Dict[str, Any]] = None
    trace: List[Dict[str, Any]] = field(default_factory=list)

    def add_step(self, description: str, tool: str = None, args: Dict[str, Any] = None):
        self.steps.append(PlanStep(description=description, tool=tool, args=args))

    def set_result(self, step_index: int, result: Any):
        self.steps[step_index].result = result

    def log(self, event: str, data: Dict[str, Any] = None):
        self.trace.append({
            "event": event,
            "data": data or {}
        })
