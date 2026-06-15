# brain/c3/memory/retriever.py

from __future__ import annotations
from typing import List

from .embeddings import EmbeddingService
from .store import InMemoryStore


class MemoryRetriever:
    """
    Thin wrapper for backward compatibility and new architecture.
    Exposes .retrieve(query: str) -> List[str].
    """

    def __init__(self, store: InMemoryStore, embedder: EmbeddingService | None = None):
        self.store = store
        self.embedder = embedder or EmbeddingService()

    def retrieve(self, query: str) -> List[str]:
        embedding = self.embedder.embed(query)
        results = self.store.search(query_embedding=embedding, top_k=5)
        return [r.record.content for r in results]
