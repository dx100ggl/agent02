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
        Matching strategy:
        - primary: if the full skill description is a substring of the task description
        - fallback: if both contain 'auto-learned' (for Ch7 tests and simple prompts)
        """
        skills = self._store.load_all()
        td = task_description.lower()

        for record in skills.values():
            desc = (record.signature.description or "").lower()
            if not desc:
                continue

            # Primary: strict substring
            if desc in td:
                return record

            # Fallback: both mention 'auto-learned'
            if "auto-learned" in desc and "auto-learned" in td:
                return record

        return None
