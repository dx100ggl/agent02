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
        Matching strategy (S4):
        1) Use embedding-based search via SkillStore.search
        2) Fallback to description/name substring heuristics
        """
        td = task_description.lower()

        # 1) Embedding-based search
        candidates = self._store.search(task_description, top_k=5)
        if candidates:
            return candidates[0]

        # 2) Heuristic fallback over all skills
        skills = self._store.load_all()
        for record in skills.values():
            desc = (record.signature.description or "").lower()
            name = (record.signature.name or "").lower()

            if desc and desc in td:
                return record
            if name and name in td:
                return record
            if "auto-learned" in desc and "auto-learned" in td:
                return record

        return None
