from __future__ import annotations

import uuid
from dataclasses import replace
from typing import Any, Dict, List, Optional

from .base import (
    EmbeddingModel,
    MemoryProvider,
    MemoryQuery,
    MemoryRecord,
    MemorySearchResult,
    MemoryStore,
)
from .embeddings import DummyEmbeddingModel
from .store import InMemoryStore


class SimpleMemoryProvider(MemoryProvider):
    """
    Default C3 memory façade:
    - uses an EmbeddingModel to embed content and queries
    - uses a MemoryStore to persist and search records
    """

    def __init__(
        self,
        store: Optional[MemoryStore] = None,
        embedding_model: Optional[EmbeddingModel] = None,
    ) -> None:
        self._store = store or InMemoryStore()
        self._embeddings = embedding_model or DummyEmbeddingModel()

    def write(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        record_id: Optional[str] = None,
    ) -> MemoryRecord:
        rid = record_id or str(uuid.uuid4())
        embedding = self._embeddings.embed_text(content)
        record = MemoryRecord(
            id=rid,
            content=content,
            metadata=metadata or {},
            embedding=embedding,
        )
        self._store.add(record)
        return replace(record)

    def search(self, query: MemoryQuery) -> List[MemorySearchResult]:
        query_embedding = self._embeddings.embed_text(query.query)
        return self._store.search(
            query_embedding=query_embedding,
            top_k=query.top_k,
            metadata_filter=query.metadata_filter,
        )

    def delete(self, record_id: str) -> None:
        self._store.delete(record_id)

    def stats(self) -> Dict[str, Any]:
        return self._store.stats()
