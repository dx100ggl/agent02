# brain/c5/beliefs/belief_store.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid


@dataclass
class Belief:
    id: str
    kind: str
    metadata: Dict[str, Any]
    strength: float
    cluster_id: Optional[str]
    created_at: datetime
    updated_at: datetime


class InMemoryBeliefStore:
    def __init__(self):
        self._beliefs: Dict[str, Belief] = {}

    # CH8 tests expect this
    def create(self, kind: str, metadata: Dict[str, Any], strength: float, cluster_id: Optional[str]):
        now = datetime.now(timezone.utc).isoformat()
        return Belief(
            id=str(uuid.uuid4()),
            kind=kind,
            metadata=metadata,
            strength=strength,
            cluster_id=cluster_id,
            created_at=now,
            updated_at=now,
        )

    def add(self, belief: Belief):
        self._beliefs[belief.id] = belief

    def update(self, belief: Belief):
        belief.updated_at = datetime.now(timezone.utc).isoformat()
        self._beliefs[belief.id] = belief

    def get(self, belief_id: str) -> Optional[Belief]:
        return self._beliefs.get(belief_id)

    def all(self) -> List[Belief]:
        return list(self._beliefs.values())

    def clear(self):
        self._beliefs.clear()
