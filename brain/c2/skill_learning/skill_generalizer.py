# brain/c2/skill_learning/skill_generalizer.py

from __future__ import annotations

from typing import List, Tuple

from brain.c2.skill_learning.skill_trace import SkillTrace
from brain.c2.skill_learning.skill_types import SkillSignature, SkillPolicy


class SkillGeneralizer:
    """
    Turns a cluster of similar traces into a single generalized skill.
    For now:
    - uses the first trace as the template
    - uses its params keys as input slots
    - uses a single logical "result" output
    """

    def generalize(self, traces: List[SkillTrace]) -> Tuple[SkillSignature, SkillPolicy]:
        if not traces:
            raise ValueError("Cannot generalize from empty trace list")

        example = traces[0]
        task_id = example.task_id

        signature = SkillSignature(
            name=f"skill_{task_id}",
            inputs=list(example.steps[0].params.keys()) if example.steps else [],
            outputs=["result"],
            description=f"Auto-learned skill for {task_id}",
        )

        policy = example.to_policy()
        return signature, policy
