from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MetaConfig:
    """
    Light-touch configuration for C6 (Option C).

    This is intentionally small and can be extended without breaking callers.
    """

    enable_reflection_hints: bool = True
    enable_efficiency_hints: bool = True
    max_steps_before_efficiency_warning: int = 4
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetaSignal:
    """
    What C6 sees for a single turn.

    Built from the orchestrator's local data; no tight coupling to C5 internals.
    """

    user_input: str
    planner_trace: List[Any]
    executor_trace: List[Any]
    final_output: Any
    error: Any
    trace_log: List[str]
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetaDecision:
    """
    What C6 suggests based on a MetaSignal.

    Orchestrator is free to ignore or only log these suggestions.
    """

    # High-level meta suggestions
    should_reflect_next_turn: bool = False
    increase_planning_depth: bool = False
    reduce_tool_calls: bool = False

    # Human-readable reason / notes
    reason: Optional[str] = None
    notes: Dict[str, Any] = field(default_factory=dict)
