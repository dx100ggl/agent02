# brain/c2/skill_learning/skill_store.py

from __future__ import annotations

import json
from typing import Dict, Optional
from typing import List
from brain.c3.memory.base import MemoryProvider, MemoryQuery
from brain.c2.skill_learning.skill_types import SkillRecord


class SkillStore:
    """
    S4 SkillStore:
    - Stores SkillRecord objects in C3 memory as JSON strings
    - Retrieves them by metadata filters
    """

    def __init__(self, memory: MemoryProvider):
        self._memory = memory

    def _metadata_for_record(self, record: SkillRecord) -> Dict[str, str]:
        return {
            "type": "skill",
            "name": record.signature.name,
            "version": str(record.version),
        }

    def _serialize(self, record: SkillRecord) -> str:
        return json.dumps(record.to_dict())

    def _deserialize(self, text: str) -> SkillRecord:
        data = json.loads(text)
        return SkillRecord.from_dict(data)

    def save(self, record: SkillRecord) -> None:
        metadata = self._metadata_for_record(record)
        serialized = self._serialize(record)
        self._memory.write(content=serialized, metadata=metadata)

    def load_all(self) -> Dict[str, SkillRecord]:
        """
        Load all skills from C3 memory.
        Returns a dict keyed by skill name (latest version wins).
        """
        mq = MemoryQuery(
            query="skill",  # non-empty so embedding is non-zero
            top_k=500,
            metadata_filter={"type": "skill"},
        )
        results = self._memory.search(mq)

        skills: Dict[str, SkillRecord] = {}
        for r in results:
            text = r.record.content
            try:
                record = self._deserialize(text)
                skills[record.signature.name] = record
            except Exception:
                continue

        return skills

    def get(self, name: str) -> Optional[SkillRecord]:
        mq = MemoryQuery(
            query=name,
            top_k=1,
            metadata_filter={
                "type": "skill",
                "name": name,
            },
        )
        results = self._memory.search(mq)
        if not results:
            return None

        text = results[0].record.content
        try:
            return self._deserialize(text)
        except Exception:
            return None

    def search(self, query: str, top_k: int = 5) -> List[SkillRecord]:
        """
        Embedding-based search over skills using C3 memory.
        """
        mq = MemoryQuery(
            query=query,
            top_k=top_k,
            metadata_filter={"type": "skill"},
        )
        results = self._memory.search(mq)

        skills: List[SkillRecord] = []
        for r in results:
            try:
                skills.append(self._deserialize(r.record.content))
            except Exception:
                continue
        return skills