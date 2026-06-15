# brain/c1/state.py

from __future__ import annotations
from typing import Any, Dict, List, Optional


class State:
    """
    Unified state object used across C1 → C2 → C3 → C5.
    Tests expect:
        State(task_id="t1", user_input="hello world")
    """

    def __init__(
        self,
        user_input: str,
        task_id: Optional[str] = None,
        user_id: Optional[str] = None,
        memory_results: Optional[Any] = None,
    ):
        # Core fields
        self.user_input = user_input
        self.task_id = task_id
        self.user_id = user_id

        # Memory retrieval results (optional)
        self.memory_results = memory_results

        # Execution context
        self.context: Dict[str, Any] = {}

        # Planner + executor traces
        self.plan = None
        self.plan_visualization: Optional[str] = None

        # Metadata (intent, reflection, meta decisions, etc.)
        self.meta: Dict[str, Any] = {}

        # History of turns (tests expect this to exist)
        self.history: List[Dict[str, Any]] = []

        # Completion flag
        self.done: bool = False
