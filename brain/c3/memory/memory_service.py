# brain/c3/memory/memory_service.py

from __future__ import annotations
from typing import List

from brain.c3.memory.store import MemoryStore
from brain.c3.memory.retriever import MemoryRetriever


class MemoryService:
    """
    Thin C3 wrapper combining store + retriever.
    """

    def __init__(self, store: MemoryStore, retriever: MemoryRetriever):
        self.store = store
        self.retriever = retriever

    def retrieve(self, query: str) -> List[str]:
        """
        Returns a list of memory snippets relevant to the query.
        """
        return self.retriever.retrieve(query)
