from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import math
import time

from brain.c3.memory.embeddings import SimpleEmbedder


@dataclass
class MemoryItem:
    id: int
    text: str
    vector: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


class MemoryStore:
    """
    In-memory vector store with simple hybrid retrieval.

    - Stores (text, vector, metadata).
    - Supports semantic similarity + keyword + recency.
    """

    def __init__(self, embedder: Optional[SimpleEmbedder] = None):
        self.embedder = embedder or SimpleEmbedder()
        self._items: List[MemoryItem] = []
        self._next_id = 1

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------
    def add(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> MemoryItem:
        vec = self.embedder.embed(text)
        item = MemoryItem(
            id=self._next_id,
            text=text,
            vector=vec,
            metadata=metadata or {},
        )
        self._next_id += 1
        self._items.append(item)
        return item

    def all_items(self) -> List[MemoryItem]:
        return list(self._items)

    def search(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        if not self._items or not query:
            return []

        q_vec = self.embedder.embed(query)
        now = time.time()
        query_lower = query.lower()

        scored: List[tuple[float, MemoryItem]] = []
        for item in self._items:
            sim = self._cosine(q_vec, item.vector)

            # Keyword bonus
            # Token-level keyword match
            query_tokens = set(query_lower.split())
            item_tokens = set(item.text.lower().split())

            token_overlap = query_tokens.intersection(item_tokens)
            kw_bonus = 1.0 if token_overlap else 0.0


            # Recency bonus (very mild)
            age = max(now - item.created_at, 1.0)
            recency_bonus = 0.05 / math.log(age + 1.0)

            score = sim + kw_bonus + recency_bonus
            scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored[:top_k]]

    # ----------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------
    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) or 1.0
        nb = math.sqrt(sum(y * y for y in b)) or 1.0
        return dot / (na * nb)
    
    # ----------------------------------------------------------
    # Legacy API compatibility
    # ----------------------------------------------------------
    def query(self, text: str, top_k: int = 5):
        """
        Legacy API used by older tests.

        Must return:
            [{"text": "...", "metadata": {...}, "id": ...}, ...]

        NOT MemoryItem objects.
        """
        items = self.search(text, top_k=top_k)
        results = []
        for item in items:
            results.append({
                "id": item.id,
                "text": item.text,
                "metadata": item.metadata,
            })
        return results


    # ----------------------------------------------------------
    # Legacy API compatibility
    # ----------------------------------------------------------
    def put(self, item: dict):
        """
        Legacy API used by older tests:
            store.put({"text": "...", "metadata": {...}})
        """
        text = item.get("text", "")
        metadata = item.get("metadata", {})
        return self.add(text, metadata)

# ----------------------------------------------------------------------
# Backward compatibility for existing code expecting LocalMemoryStore
# ----------------------------------------------------------------------
class LocalMemoryStore(MemoryStore):
    """
    Legacy alias for MemoryStore.
    Used by build_brain() and older tests.
    """
    pass

