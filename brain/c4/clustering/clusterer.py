# brain/c4/clustering/clusterer.py

from __future__ import annotations
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime, timezone
import uuid

from brain.c3.memory.store import InMemoryStore
from .cluster_store import InMemoryClusterStore, Cluster


class SimpleKeywordClusterer:
    """
    C4 clustering organ.
    Now tag-aware:
      - Uses semantic tags (if present) to boost similarity.
      - Falls back to keyword grouping when tags are absent.
    Deterministic, no LLM calls here.
    """

    def __init__(self, store: InMemoryStore, cluster_store: InMemoryClusterStore):
        self.store = store
        self.cluster_store = cluster_store

    def run(
        self,
        nodes: Optional[List[Dict[str, Any]]] = None,
        cluster_store: Optional[InMemoryClusterStore] = None,
        tag_similarity_fn: Optional[Callable[[Dict[str, Any], Dict[str, Any]], float]] = None,
    ) -> None:
        """
        Rebuild clusters using keyword + optional tag similarity.
        If nodes is None, pull from C3 store.
        """
        if nodes is None:
            snapshot = self.store.graph_snapshot()
            nodes = snapshot["nodes"]

        if cluster_store is None:
            cluster_store = self.cluster_store

        # ------------------------------------------------------------------
        # 1. Compute similarity buckets
        # ------------------------------------------------------------------
        buckets: Dict[str, List[str]] = {}

        for node in nodes:
            content = node["content"].lower()
            tokens = [
                t for t in content.split()
                if t not in {"user", "the", "a", "is", "are", "while"}
            ]

            # Base keyword key
            key = tokens[0] if tokens else "__misc__"

            # If tags exist, refine the key using tag signature
            tags = node.get("metadata", {}).get("tags", [])
            if tags:
                # Deterministic tag signature
                tag_sig = "_".join(sorted(tags))
                key = f"{key}__{tag_sig}"

            buckets.setdefault(key, []).append(node["id"])

        # ------------------------------------------------------------------
        # 2. Optional tag similarity merging
        # ------------------------------------------------------------------
        if tag_similarity_fn is not None:
            # Merge buckets whose nodes have high tag similarity
            merged_buckets: Dict[str, List[str]] = {}

            for key, node_ids in buckets.items():
                placed = False

                for mk, mk_ids in merged_buckets.items():
                    # Compare first node of each bucket (cheap heuristic)
                    n1 = next(n for n in nodes if n["id"] == node_ids[0])
                    n2 = next(n for n in nodes if n["id"] == mk_ids[0])

                    sim = tag_similarity_fn(n1, n2)
                    if sim >= 0.5:  # threshold for merging
                        mk_ids.extend(node_ids)
                        placed = True
                        break

                if not placed:
                    merged_buckets[key] = list(node_ids)

            buckets = merged_buckets

        # ------------------------------------------------------------------
        # 3. Build clusters
        # ------------------------------------------------------------------
        cluster_store.clear()
        now = datetime.now(timezone.utc).isoformat()

        for key, node_ids in buckets.items():
            cluster = Cluster(
                id=str(uuid.uuid4()),
                node_ids=node_ids,
                created_at=now,
                updated_at=now,
                label=key,
                metadata={"size": len(node_ids)},
            )
            cluster_store.add(cluster)
