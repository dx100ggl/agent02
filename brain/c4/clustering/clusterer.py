# brain/c4/clustering/clusterer.py

from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime

from brain.c3.memory.store import InMemoryStore
from .cluster_store import InMemoryClusterStore, Cluster
import uuid


class SimpleKeywordClusterer:
    """
    C4 clustering organ.
    Groups C3 nodes into clusters based on shared keywords in content.
    Deterministic, no LLM, good enough as a structural layer.
    """

    def __init__(self, store: InMemoryStore, cluster_store: InMemoryClusterStore):
        self.store = store
        self.cluster_store = cluster_store

    def run(self) -> None:
        snapshot = self.store.graph_snapshot()
        nodes: List[Dict[str, Any]] = snapshot["nodes"]

        # Very simple: group by first meaningful keyword
        buckets: Dict[str, List[str]] = {}

        for node in nodes:
            content = node["content"].lower()
            tokens = [t for t in content.split() if t not in {"user", "the", "a", "is", "are", "while"}]
            if not tokens:
                key = "__misc__"
            else:
                key = tokens[0]

            buckets.setdefault(key, []).append(node["id"])

        # Build clusters
        self.cluster_store.clear()
        now = datetime.utcnow()

        for key, node_ids in buckets.items():
            cluster = Cluster(
                id=str(uuid.uuid4()),
                node_ids=node_ids,
                created_at=now,
                updated_at=now,
                label=key,
                metadata={"size": len(node_ids)},
            )
            self.cluster_store.add(cluster)
