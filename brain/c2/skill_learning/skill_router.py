# brain/c2/skill_learning/skill_router.py

from __future__ import annotations

from typing import Any, Optional

from brain.c2.skill_learning.skill_retriever import SkillRetriever
from brain.c2.skill_learning.skill_store import SkillStore
from brain.c2.skill_learning.skill_types import SkillRecord


class SkillRouter:
    """
    Routes tasks to learned skills when possible.
    If no suitable skill or planner surface exists, returns None.
    """

    def __init__(self, store: SkillStore, planner: Any):
        # store: SkillStore
        # planner: something like AdaptivePlanner or DummyPlanner in tests
        self._store = store
        self._planner = planner
        self._retriever = SkillRetriever(store)

    def route(self, task_description: str) -> Optional[Any]:
        """
        - Try to find a matching skill
        - If found and planner supports execute(), replay it
        - Otherwise, return None and let the orchestrator fall back
        """
        skill = self._retriever.find_matching_skill(task_description)

        # Only execute skills if planner exposes an execute(action, params) surface
        if skill is not None and hasattr(self._planner, "execute"):
            return self._execute_skill(skill)

        # No skill or incompatible planner → let orchestrator continue normally
        return None

    def _execute_skill(self, skill: SkillRecord) -> Any:
        """
        Replay the skill policy via a planner that exposes execute(action, params).
        """
        result = None
        for step in skill.policy.steps:
            result = self._planner.execute(step.action, step.params)
        return result
