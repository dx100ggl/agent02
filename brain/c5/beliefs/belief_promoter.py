# brain/c5/beliefs/belief_promoter.py

from __future__ import annotations
from typing import List
from datetime import datetime, timezone
import uuid

from brain.c4.clustering.cluster_store import Cluster
from .belief_store import InMemoryBeliefStore, Belief


class SimpleBeliefPromoter:
    """
    C5 promotion organ.
    Turns stable clusters into beliefs.
    """

    def __init__(self, belief_store: InMemoryBeliefStore, min_size: int = 2):
        self.belief_store = belief_store
        self.min_size = min_size

    def promote_from_clusters(self, clusters: List[Cluster]) -> None:
        now = datetime.now(timezone.utc).isoformat()

        for cluster in clusters:
            # Simple rule: only promote clusters with at least min_size nodes
            if len(cluster.node_ids) < self.min_size:
                continue

            # Check if we already have a belief for this cluster
            existing = self.belief_store.find_by_cluster(cluster.id)
            if existing:
                # Strengthen existing belief
                belief = existing[0]
                belief.strength = min(1.0, belief.strength + 0.1)
                belief.updated_at = now
                self.belief_store.update(belief)
                continue

            # Create new belief
            content = f"Cluster '{cluster.label}' with {len(cluster.node_ids)} nodes"
            belief = Belief(
                id=str(uuid.uuid4()),
                cluster_id=cluster.id,
                content=content,
                created_at=now,
                updated_at=now,
                strength=0.5,
                metadata={"size": len(cluster.node_ids)},
            )
            self.belief_store.add(belief)
