# brain/c2/skill_learning/skill_store.py

from __future__ import annotations

import json
from typing import Dict, Optional, List
from brain.c3.memory.base import MemoryProvider, MemoryQuery
from brain.c2.skill_learning.skill_types import SkillRecord


class SkillStore:
    """
    Brain‑24 / S4 SkillStore

    Responsibilities:
    - Persist SkillRecord objects into C3 memory as JSON strings
    - Retrieve skills via metadata filters
    - Provide embedding‑based search over stored skills
    - Always return the *latest version* of each skill when loading all
    """

    def __init__(self, memory: MemoryProvider):
        self._memory = memory

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Save a skill
    # ---------------------------------------------------------
    def save(self, record: SkillRecord) -> None:
        """
        Persist a SkillRecord into C3 memory.
        Stored as a JSON string with metadata for filtering.
        """
        metadata = self._metadata_for_record(record)
        serialized = self._serialize(record)
        self._memory.write(content=serialized, metadata=metadata)

    # ---------------------------------------------------------
    # Load all skills (latest version wins)
    # ---------------------------------------------------------
    def load_all(self) -> Dict[str, SkillRecord]:
        """
        Load all skills from C3 memory.
        Returns a dict keyed by skill name, where the highest version wins.
        """
        mq = MemoryQuery(
            query="skill",  # ensures non‑zero embedding
            top_k=500,
            metadata_filter={"type": "skill"},
        )
        results = self._memory.search(mq)

        skills: Dict[str, SkillRecord] = {}

        for r in results:
            text = r.record.content
            try:
                record = self._deserialize(text)
                name = record.signature.name

                # Keep the highest version
                if name not in skills or record.version > skills[name].version:
                    skills[name] = record

            except Exception:
                continue

        return skills

    # ---------------------------------------------------------
    # Get a single skill by name (latest version)
    # ---------------------------------------------------------
    def get(self, name: str) -> Optional[SkillRecord]:
        mq = MemoryQuery(
            query=name,
            top_k=5,
            metadata_filter={"type": "skill", "name": name},
        )
        results = self._memory.search(mq)
        if not results:
            return None

        best: Optional[SkillRecord] = None

        for r in results:
            try:
                record = self._deserialize(r.record.content)
                if best is None or record.version > best.version:
                    best = record
            except Exception:
                continue

        return best

    # ---------------------------------------------------------
    # Embedding‑based search
    # ---------------------------------------------------------
    def search(self, query: str, top_k: int = 5) -> List[SkillRecord]:
        """
        Embedding‑based search over skills using C3 memory.
        Returns a list of SkillRecord objects.
        """
        mq = MemoryQuery(
            query=query,
            top_k=top_k,
            metadata_filter={"type": "skill"},
        )
        results = self._memory.search(mq)

        out: List[SkillRecord] = []
        for r in results:
            try:
                out.append(self._deserialize(r.record.content))
            except Exception:
                continue

        return out
