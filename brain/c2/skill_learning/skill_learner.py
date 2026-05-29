# brain/c2/skill_learning/skill_learner.py

from __future__ import annotations

from typing import List

from brain.c3.memory.base import MemoryProvider
from brain.c2.skill_learning.skill_trace import SkillTrace
from brain.c2.skill_learning.skill_detector import SkillDetector
from brain.c2.skill_learning.skill_generalizer import SkillGeneralizer
from brain.c2.skill_learning.skill_store import SkillStore
from brain.c2.skill_learning.skill_types import SkillRecord


class SkillLearner:
    """
    Core Ch7 engine:
    - takes execution traces
    - detects repeated patterns
    - generalizes them into skills
    - persists them into C3 memory via SkillStore
    """

    def __init__(self, memory: MemoryProvider):
        self._detector = SkillDetector()
        self._generalizer = SkillGeneralizer()
        self._store = SkillStore(memory)

    def learn_from_traces(self, traces: List[SkillTrace]) -> List[SkillRecord]:
        """
        Main learning entrypoint.
        Returns the list of newly learned SkillRecord objects.
        """
        groups = self._detector.detect_repetition(traces)
        learned: List[SkillRecord] = []

        for group in groups:
            signature, policy = self._generalizer.generalize(group)
            record = SkillRecord(
                signature=signature,
                policy=policy,
                confidence=0.8,
                usage_count=0,
            )
            self._store.save(record)
            learned.append(record)

        return learned
