# brain/c3/memory/store.py

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Dict, List, Optional

# S4 core imports (renamed to avoid clashing with legacy MemoryStore)
from .base import MemoryRecord, MemorySearchResult, MemoryStore as BaseMemoryStore


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class InMemoryStore(BaseMemoryStore):
    """
    Simple in-process vector store.
    Good enough for S4; can be swapped for a persistent backend later.
    """

    def __init__(self) -> None:
        self._records: Dict[str, MemoryRecord] = {}

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
        return {
            "count": len(self._records),
        }


# --------------------------------------------------------------------
# Legacy compatibility layer for existing tests
# --------------------------------------------------------------------

@dataclass
class MemoryItem:
    """
    Legacy memory item used by older tests.

    Minimal surface:
    - text: str
    - tags: optional list of strings
    """
    text: str
    tags: Optional[List[str]] = None


class MemoryStore:
    """
    Legacy, text-only MemoryStore used by old tests.

    API expected by tests/test_c3_memory_store.py:
        m = MemoryStore()
        m.add("cats are cute", tags=["animal"])
        results = m.search("cats")
        results[0].text -> "cats are cute"
    """

    def __init__(self) -> None:
        self._items: List[MemoryItem] = []

    def add(self, text: str, tags: Optional[List[str]] = None) -> None:
        self._items.append(MemoryItem(text=text, tags=tags))

    def search(self, query: str) -> List[MemoryItem]:
        q = query.lower()
        return [item for item in self._items if q in item.text.lower()]
