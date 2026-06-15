# brain/c4/clustering/cluster_store.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any
import uuid
from datetime import datetime


@dataclass
class Cluster:
    id: str
    node_ids: List[str]
    created_at: datetime
    updated_at: datetime
    label: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class InMemoryClusterStore:
    """
    Simple in-memory store for C4 clusters.
    """

    def __init__(self) -> None:
        self._clusters: Dict[str, Cluster] = {}

    def add(self, cluster: Cluster) -> None:
        self._clusters[cluster.id] = cluster

    def update(self, cluster: Cluster) -> None:
        self._clusters[cluster.id] = cluster

    def all(self) -> List[Cluster]:
        return list(self._clusters.values())

    def clear(self) -> None:
        self._clusters.clear()
