# brain/c4/synthesizer/modifiers.py

from dataclasses import dataclass
from typing import List, Any

@dataclass(frozen=True)
class BeliefModifiers:
    concise: bool = False
    detailed: bool = False
    expert: bool = False
    shallow_reasoning: bool = False


def normalize_beliefs(beliefs: List[Any]) -> BeliefModifiers:
    return BeliefModifiers(
        concise=any(
            b.kind == "preference" and "concise" in b.metadata.get("tags", [])
            for b in beliefs
        ),
        detailed=any(
            b.kind == "preference" and "detailed" in b.metadata.get("tags", [])
            for b in beliefs
        ),
        expert=any(b.kind == "skill" for b in beliefs),
        shallow_reasoning=any(getattr(b, "strength", 0) >= 0.8 for b in beliefs),
    )
