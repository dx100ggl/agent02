# brain/c5/memory_layer.py

from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime
import uuid

from brain.c4.clustering.cluster_store import InMemoryClusterStore, Cluster
from brain.c5.beliefs.belief_store import InMemoryBeliefStore, Belief


class C5BeliefLayer:
    """
    C5 organ: promotes C4 clusters into stable beliefs.
    Tag-aware, deterministic, and compatible with the existing Belief model.
    """

    def __init__(self, cluster_store: InMemoryClusterStore):
        self.cluster_store = cluster_store
        self.belief_store = InMemoryBeliefStore()

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def rebuild_beliefs(self) -> None:
        """
        Rebuild beliefs from C4 clusters.
        Strengthens existing beliefs, creates new ones when needed.
        """
        clusters = self.cluster_store.all()
        now = datetime.utcnow()

        for cluster in clusters:
            tags = cluster.metadata.get("tags", [])

            # Infer belief type from tags
            kind = self._infer_kind(tags)
            if kind is None:
                continue

            # Check if belief already exists for this cluster
            existing = self.belief_store.find_by_cluster(cluster.id)
            if existing:
                belief = existing[0]
                belief.strength = min(1.0, belief.strength + 0.1)
                belief.updated_at = now
                self.belief_store.update(belief)
                continue

            # Create new belief
            content = f"Cluster '{cluster.label}' expresses a user {kind}"
            belief = Belief(
                id=str(uuid.uuid4()),
                cluster_id=cluster.id,
                content=content,
                created_at=now,
                updated_at=now,
                strength=0.5,
                metadata={
                    "tags": tags,
                    "size": cluster.metadata.get("size", 0),
                    "kind": kind,
                },
            )
            self.belief_store.add(belief)

    def get_beliefs(self) -> List[Belief]:
        return self.belief_store.all()

    # ------------------------------------------------------------------
    # INTERNAL LOGIC
    # ------------------------------------------------------------------

    def _infer_kind(self, tags: List[str]) -> str | None:
        """
        Infer belief type from semantic tags.
        """
        lower = [t.lower() for t in tags]

        if any(t in lower for t in ["preference", "likes", "enjoys"]):
            return "preference"

        if any(t in lower for t in ["skill", "expertise"]):
            return "skill"

        if any(t in lower for t in ["constraint", "limit", "avoid"]):
            return "constraint"

        if any(t in lower for t in ["habit", "routine"]):
            return "habit"

        return None
