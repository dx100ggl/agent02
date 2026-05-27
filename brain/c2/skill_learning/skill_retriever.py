# brain/c2/skill_learning/skill_retriever.py

from __future__ import annotations

from typing import Optional

from brain.c2.skill_learning.skill_store import SkillStore
from brain.c2.skill_learning.skill_types import SkillRecord


class SkillRetriever:
    """
    Retrieval surface for C2:
    - given a task description, try to find a matching skill
    """

    def __init__(self, store: SkillStore):
        self._store = store

    def find_matching_skill(self, task_description: str) -> Optional[SkillRecord]:
        """
        Extremely simple matching:
        - if the skill description is a substring of the task description,
          we treat it as a match.

        This can later be upgraded to embedding similarity, tags, etc.
        """
        skills = self._store.load_all()
        for record in skills.values():
            desc = (record.signature.description or "").lower()
            if desc and desc in task_description.lower():
                return record
        return None
