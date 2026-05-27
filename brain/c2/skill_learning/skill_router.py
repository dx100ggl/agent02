# brain/c2/skill_learning/skill_router.py

from __future__ import annotations

from typing import Any

from brain.c2.skill_learning.skill_retriever import SkillRetriever
from brain.c2.skill_learning.skill_store import SkillStore
from brain.c2.skill_learning.skill_types import SkillRecord


class SkillRouter:
    """
    C2 entrypoint for using learned skills:
    - given a task description, first try to route via a learned skill
    - if no skill matches, fall back to the normal planner path

    This expects:
    - store: SkillStore
    - planner: object with .plan(task_description: str) -> Any
               and .execute(action: str, params: dict) -> Any
    """

    def __init__(self, store: SkillStore, planner):
        self._store = store
        self._retriever = SkillRetriever(store)
        self._planner = planner

    def route(self, task_description: str) -> Any:
        """
        Main routing method:
        - try to find a matching skill
        - if found, execute it
        - otherwise, delegate to planner.plan(...)
        """
        skill = self._retriever.find_matching_skill(task_description)

        if skill is not None:
            return self._execute_skill(skill)

        return self._planner.plan(task_description)

    def _execute_skill(self, skill: SkillRecord) -> Any:
        """
        Replay the skill policy via the planner/executor surface.
        """
        result: Any = None
        for step in skill.policy.steps:
            # Planner is assumed to expose an execute(action, params) surface.
            result = self._planner.execute(step.action, step.params)
        return result

