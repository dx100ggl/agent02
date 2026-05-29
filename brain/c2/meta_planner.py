# C2 Meta-Planner (Ch6)
# Controls HOW planning should occur before C1 executes it.

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


class PlanningMode(Enum):
    SINGLE_STEP = "single_step"
    MULTI_STEP = "multi_step"
    TOOL_AWARE = "tool_aware"
    MEMORY_AWARE = "memory_aware"
    HYBRID = "hybrid"


@dataclass
class C2Directive:
    mode: PlanningMode
    notes: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None


class C2MetaPlanner:
    """
    The C2 Meta-Planner decides HOW planning should occur.
    It does not generate the plan itself — that is C1's job.
    """

    def decide_planning_mode(self, user_input: str) -> PlanningMode:
        text = user_input.lower()

        if "calculate" in text or "compute" in text:
            return PlanningMode.TOOL_AWARE

        if "steps" in text or "process" in text or "how to" in text:
            return PlanningMode.MULTI_STEP

        if "remember" in text or "recall" in text:
            return PlanningMode.MEMORY_AWARE

        return PlanningMode.SINGLE_STEP

    def generate_schema(self, mode: PlanningMode) -> Dict[str, Any]:
        if mode == PlanningMode.SINGLE_STEP:
            return {"type": "single_step", "steps": ["Produce a direct answer."]}

        if mode == PlanningMode.MULTI_STEP:
            return {
                "type": "multi_step",
                "steps": [
                    "Identify subproblems.",
                    "Solve each subproblem.",
                    "Integrate results.",
                ],
            }

        if mode == PlanningMode.TOOL_AWARE:
            return {
                "type": "tool_aware",
                "steps": [
                    "Determine which tool is needed.",
                    "Prepare tool input.",
                    "Call tool.",
                    "Interpret tool output.",
                    "Produce final answer.",
                ],
            }

        if mode == PlanningMode.MEMORY_AWARE:
            return {
                "type": "memory_aware",
                "steps": [
                    "Check memory relevance.",
                    "Retrieve relevant memory.",
                    "Integrate memory into reasoning.",
                    "Produce final answer.",
                ],
            }

        return {
            "type": "hybrid",
            "steps": [
                "Analyze task.",
                "Select combination of planning modes.",
                "Generate hybrid plan.",
                "Execute hybrid plan.",
            ],
        }

    def create_directive(self, user_input: str) -> C2Directive:
        mode = self.decide_planning_mode(user_input)
        schema = self.generate_schema(mode)
        return C2Directive(
            mode=mode,
            notes=f"C2 selected planning mode: {mode.value}",
            schema=schema,
        )
