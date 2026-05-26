# brain/c3/memory/store.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import math
import time

from brain.c3.memory.embeddings import SimpleEmbedder


# ----------------------------------------------------------
# Memory item
# ----------------------------------------------------------

@dataclass
class MemoryItem:
    id: int
    text: str
    vector: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


# ----------------------------------------------------------
# Memory store
# ----------------------------------------------------------

class MemoryStore:
    """
    In-memory vector store with hybrid retrieval.

    IMPORTANT:
    - search() returns MemoryItem objects (tests require this)
    - write_fact() is an alias for add()
    - legacy query() returns dicts
    """

    def __init__(self, embedder: Optional[SimpleEmbedder] = None):
        self.embedder = embedder or SimpleEmbedder()
        self._items: List[MemoryItem] = []
        self._next_id = 1

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def write_fact(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> MemoryItem:
        """
        New API used by write_memory_tool.
        """
        return self.add(text, metadata)

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

    # ----------------------------------------------------------
    # Hybrid search (semantic + keyword + recency)
    # ----------------------------------------------------------

    def search(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """
        Returns MemoryItem objects (NOT dicts).
        Tests expect item.text and item.vector.
        """
        if not self._items or not query:
            return []

        q_vec = self.embedder.embed(query)
        now = time.time()
        query_lower = query.lower()
        query_tokens = set(query_lower.split())

        scored: List[tuple[float, MemoryItem]] = []

        for item in self._items:
            # Semantic similarity
            sim = self._cosine(q_vec, item.vector)

            # Keyword bonus
            item_tokens = set(item.text.lower().split())
            kw_bonus = 1.0 if query_tokens.intersection(item_tokens) else 0.0

            # Recency bonus
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
        """
        items = self.search(text, top_k=top_k)
        return [
            {"id": item.id, "text": item.text, "metadata": item.metadata}
            for item in items
        ]

    def put(self, item: dict):
        """
        Legacy API used by older tests:
            store.put({"text": "...", "metadata": {...}})
        """
        text = item.get("text", "")
        metadata = item.get("metadata", {})
        return self.add(text, metadata)


# ----------------------------------------------------------
# Legacy alias
# ----------------------------------------------------------

class LocalMemoryStore(MemoryStore):
    pass
