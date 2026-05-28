# brain/c2/skill_learning/skill_types.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


# ============================================================
# Skill Signature
# ============================================================
@dataclass
class SkillSignature:
    name: str
    inputs: List[str]
    outputs: List[str]
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "description": self.description,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SkillSignature":
        return SkillSignature(
            name=data["name"],
            inputs=list(data.get("inputs", [])),
            outputs=list(data.get("outputs", [])),
            description=data.get("description", ""),
        )


# ============================================================
# Skill Policy Step
# ============================================================
@dataclass
class SkillPolicyStep:
    action: str
    params: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "params": self.params,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SkillPolicyStep":
        return SkillPolicyStep(
            action=data["action"],
            params=dict(data.get("params", {})),
        )


# ============================================================
# Skill Policy
# ============================================================
@dataclass
class SkillPolicy:
    steps: List[SkillPolicyStep] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "steps": [s.to_dict() for s in self.steps],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SkillPolicy":
        return SkillPolicy(
            steps=[SkillPolicyStep.from_dict(s) for s in data.get("steps", [])]
        )


# ============================================================
# Skill Record
# ============================================================
@dataclass
class SkillRecord:
    signature: SkillSignature
    policy: SkillPolicy
    version: int = 1
    confidence: float = 0.0
    usage_count: int = 0
    last_used: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signature": self.signature.to_dict(),
            "policy": self.policy.to_dict(),
            "version": self.version,
            "confidence": self.confidence,
            "usage_count": self.usage_count,
            "last_used": self.last_used,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SkillRecord":
        return SkillRecord(
            signature=SkillSignature.from_dict(data["signature"]),
            policy=SkillPolicy.from_dict(data["policy"]),
            version=data.get("version", 1),
            confidence=data.get("confidence", 0.0),
            usage_count=data.get("usage_count", 0),
            last_used=data.get("last_used"),
        )
