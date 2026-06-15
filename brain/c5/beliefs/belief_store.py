# brain/c5/beliefs/belief_store.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime
import uuid


@dataclass
class Belief:
    id: str
    cluster_id: str
    content: str
    created_at: datetime
    updated_at: datetime
    strength: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class InMemoryBeliefStore:
    """
    Simple in-memory store for C5 beliefs.
    """

    def __init__(self) -> None:
        self._beliefs: Dict[str, Belief] = {}

    def add(self, belief: Belief) -> None:
        self._beliefs[belief.id] = belief

    def update(self, belief: Belief) -> None:
        self._beliefs[belief.id] = belief

    def all(self) -> List[Belief]:
        return list(self._beliefs.values())

    def find_by_cluster(self, cluster_id: str) -> List[Belief]:
        return [b for b in self._beliefs.values() if b.cluster_id == cluster_id]

    def clear(self) -> None:
        self._beliefs.clear()
