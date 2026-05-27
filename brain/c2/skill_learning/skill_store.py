# brain/c2/skill_learning/skill_store.py

from __future__ import annotations

from typing import Dict, Optional

from brain.c2.skill_learning.skill_types import SkillRecord


class SkillStore:
    """
    Thin adapter over the existing C3 MemoryStore.
    Expects a memory object with:
    - write(key: str, value: Any) -> None
    - read(key: str) -> Any | None
    - scan(prefix: str) -> Dict[str, Any]
    """

    def __init__(self, memory):
        self._memory = memory

    def _key_for_record(self, record: SkillRecord) -> str:
        return f"skill::{record.signature.name}::v{record.version}"

    def _key_for_name(self, name: str) -> str:
        # Latest version lookup can be implemented later; for now assume v1
        return f"skill::{name}::v1"

    def save(self, record: SkillRecord) -> None:
        key = self._key_for_record(record)
        self._memory.write(key, record)

    def load_all(self) -> Dict[str, SkillRecord]:
        raw = self._memory.scan(prefix="skill::")
        # Assume memory returns a dict[str, SkillRecord] or compatible
        return dict(raw)

    def get(self, name: str) -> Optional[SkillRecord]:
        key = self._key_for_name(name)
        value = self._memory.read(key)
        if isinstance(value, SkillRecord):
            return value
        return None
