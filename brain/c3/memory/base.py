from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class MemoryRecord:
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    embedding: Optional[List[float]] = None   # <-- THIS MUST EXIST


@dataclass
class MemoryQuery:
    query: str
    top_k: int = 5
    metadata_filter: Optional[Dict[str, Any]] = None


@dataclass
class MemorySearchResult:
    record: MemoryRecord
    score: float


class EmbeddingModel(Protocol):
    def embed_text(self, text: str) -> List[float]:
        ...


class MemoryStore(ABC):
    @abstractmethod
    def add(self, record: MemoryRecord) -> None:
        ...

    @abstractmethod
    def add_many(self, records: List[MemoryRecord]) -> None:
        ...

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[MemorySearchResult]:
        ...

    @abstractmethod
    def delete(self, record_id: str) -> None:
        ...

    @abstractmethod
    def get(self, record_id: str) -> Optional[MemoryRecord]:
        ...

    @abstractmethod
    def stats(self) -> Dict[str, Any]:
        ...


class MemoryRetriever(ABC):
    @abstractmethod
    def search(self, query: MemoryQuery) -> List[MemorySearchResult]:
        ...


class MemoryProvider(ABC):
    """
    High-level façade for C3 memory used by tools, C2, and C5.
    """

    @abstractmethod
    def write(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        record_id: Optional[str] = None,
    ) -> MemoryRecord:
        ...

    @abstractmethod
    def search(self, query: MemoryQuery) -> List[MemorySearchResult]:
        ...

    @abstractmethod
    def delete(self, record_id: str) -> None:
        ...

    @abstractmethod
    def stats(self) -> Dict[str, Any]:
        ...
