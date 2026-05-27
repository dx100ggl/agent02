# brain/c2/skill_learning/skill_detector.py

from __future__ import annotations

from typing import Dict, List, Tuple

from brain.c2.skill_learning.skill_trace import SkillTrace


class SkillDetector:
    """
    Very simple repetition detector:
    - groups traces by their action sequence
    - returns only groups with more than one trace
    """

    def _pattern_key(self, trace: SkillTrace) -> Tuple[str, ...]:
        return tuple(step.action for step in trace.steps)

    def detect_repetition(self, traces: List[SkillTrace]) -> List[List[SkillTrace]]:
        clusters: Dict[Tuple[str, ...], List[SkillTrace]] = {}
        for t in traces:
            key = self._pattern_key(t)
            clusters.setdefault(key, []).append(t)
        return [group for group in clusters.values() if len(group) > 1]

