# brain/c4/memory_layer.py

from typing import Optional, List, Dict, Any
from brain.c3.memory.store import InMemoryStore
from brain.c4.clustering.cluster_store import InMemoryClusterStore
from brain.c4.clustering.clusterer import SimpleKeywordClusterer
from brain.c4.semantic_annotator import SemanticAnnotator


class C4SemanticLayer:
    def __init__(
        self,
        c3_store,
        clusterer,
        cluster_store,
        annotator: Optional[SemanticAnnotator] = None,
    ):
        self._store = c3_store
        self._clusterer = clusterer
        self._cluster_store = cluster_store
        self._annotator = annotator

    def rebuild_clusters(self) -> None:
        """
        Rebuild clusters from the current C3 graph.
        Optionally annotate nodes with semantic tags first.
        """
        snapshot = self._store.graph_snapshot()
        nodes: List[Dict[str, Any]] = snapshot.get("nodes", [])

        if self._annotator is not None:
            self._annotator.annotate_nodes(nodes)

        # existing clustering logic using self._clusterer and self._cluster_store
        self._clusterer.run(
            nodes,
            self._cluster_store,
            tag_similarity_fn=self._tag_similarity if hasattr(self, "_tag_similarity") else None,
        )


    def get_clusters(self):
        return self.cluster_store.all()

    def _tag_similarity(self, node_a, node_b) -> float:
        """
        Compute a simple tag-based similarity score between two nodes.
        Returns a value in [0, 1].
        """
        tags_a = set(node_a.get("metadata", {}).get("tags", []))
        tags_b = set(node_b.get("metadata", {}).get("tags", []))

        if not tags_a or not tags_b:
            return 0.0

        # Jaccard similarity between tag sets
        intersection = tags_a.intersection(tags_b)
        union = tags_a.union(tags_b)

        return len(intersection) / len(union)
