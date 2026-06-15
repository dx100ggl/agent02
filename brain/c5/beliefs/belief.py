# brain/c5/beliefs/belief.py

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Belief:
    id: str
    content: str
    kind: str  # "preference", "skill", "constraint", "habit", etc.
    metadata: Dict[str, Any]
