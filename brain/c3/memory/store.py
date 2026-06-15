# brain/c3/memory/store.py

from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict, List, Optional

from .base import MemoryRecord, MemorySearchResult, MemoryStore


def _cosine_similarity(a, b) -> float:
    # Handle None or empty
    if a is None or b is None:
        return 0.0

    # Convert numpy arrays to lists if needed
    if hasattr(a, "tolist"):
        a = a.tolist()
    if hasattr(b, "tolist"):
        b = b.tolist()

    if len(a) == 0 or len(b) == 0 or len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)

class InMemoryStore(MemoryStore):
    """
    Dual-mode store:
      - Vector store for MemoryRecord (used by MemoryRetriever)
      - Graph store for consolidation nodes (used by ConsolidationEngine)
    """

    def __init__(self) -> None:
        # Vector store
        self._records: Dict[str, MemoryRecord] = {}

        # Graph store for consolidation
        self._graph_nodes: Dict[str, Dict[str, Any]] = {}

    # ----------------------------------------------------------------------
    # VECTOR STORE API (unchanged)
    # ----------------------------------------------------------------------

    def add(self, record: MemoryRecord) -> None:
        self._records[record.id] = record

    def add_many(self, records: List[MemoryRecord]) -> None:
        for r in records:
            self.add(r)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[MemorySearchResult]:
        results: List[MemorySearchResult] = []

        for record in self._records.values():
            if metadata_filter:
                if not all(record.metadata.get(k) == v for k, v in metadata_filter.items()):
                    continue

            if record.embedding is None:
                continue

            score = _cosine_similarity(query_embedding, record.embedding)
            if score <= 0.0:
                continue

            results.append(MemorySearchResult(record=record, score=score))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def delete(self, record_id: str) -> None:
        self._records.pop(record_id, None)

    def get(self, record_id: str) -> Optional[MemoryRecord]:
        record = self._records.get(record_id)
        return replace(record) if record is not None else None

    def stats(self) -> Dict[str, Any]:
        return {"count": len(self._records)}

    # ----------------------------------------------------------------------
    # GRAPH STORE API (NEW)
    # ----------------------------------------------------------------------

    def add_node(self, node: Dict[str, Any]) -> None:
        self._graph_nodes[node["id"]] = node

    def update_node(self, node: Dict[str, Any]) -> None:
        self._graph_nodes[node["id"]] = node

    def find_similar(self, embedding: List[float], threshold: float):
        """
        Return list of (node, score) for nodes above threshold.
        """
        results = []
        for node in self._graph_nodes.values():
            score = _cosine_similarity(embedding, node["embedding"])
            if score >= threshold:
                results.append((node, score))
        return results

    def graph_snapshot(self) -> Dict[str, Any]:
        """
        Return a simple snapshot of the consolidation graph.
        """
        return {
            "nodes": list(self._graph_nodes.values()),
            "count": len(self._graph_nodes),
        }
