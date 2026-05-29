# brain/c2/skill_learning/skill_trace.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from brain.c2.skill_learning.skill_types import SkillPolicy, SkillPolicyStep


@dataclass
class TraceStep:
    """
    One executed step in a trace:
    - action: symbolic action name
    - params: parameters used
    - result: raw result (opaque to the learner)
    """
    action: str
    params: Dict[str, Any]
    result: Any


@dataclass
class SkillTrace:
    """
    A trace of a multi-step behavior that may become a skill.
    """
    task_id: str
    steps: List[TraceStep]

    def to_policy(self) -> SkillPolicy:
        """
        Convert this trace into a naive policy by stripping results
        and keeping only (action, params).
        """
        return SkillPolicy(
            steps=[
                SkillPolicyStep(action=s.action, params=s.params)
                for s in self.steps
            ]
        )
