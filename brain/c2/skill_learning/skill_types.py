# brain/c2/skill_learning/skill_types.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SkillSignature:
    """
    Structural description of a learned skill:
    - name: stable identifier
    - inputs: logical input slots (names)
    - outputs: logical output slots (names)
    - description: natural language description for retrieval / matching
    """
    name: str
    inputs: List[str]
    outputs: List[str]
    description: str = ""


@dataclass
class SkillPolicyStep:
    """
    One step in a skill policy:
    - action: symbolic action name (e.g. tool name, planner op)
    - params: parameter dict passed to the executor / planner
    """
    action: str
    params: Dict[str, Any]


@dataclass
class SkillPolicy:
    """
    A skill policy is a sequence of steps that can be replayed
    by the executor / planner.
    """
    steps: List[SkillPolicyStep]


@dataclass
class SkillRecord:
    """
    Persisted representation of a learned skill.
    """
    signature: SkillSignature
    policy: SkillPolicy
    version: int = 1
    confidence: float = 0.0
    usage_count: int = 0
    last_used: Optional[str] = None
