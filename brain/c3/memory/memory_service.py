# brain/c3/memory/memory_service.py

from __future__ import annotations
from typing import List, Dict, Any

from brain.c3.memory.store import MemoryStore
from brain.c3.memory.retriever import MemoryRetriever
from brain.c3.memory.embeddings import EmbeddingService
from brain.c3.memory.consolidation.consolidation_engine import ConsolidationEngine
from brain.c3.memory.base import MemoryRecord
import uuid

class MemoryService:
    """
    C3 Memory Service.
    Combines:
      - MemoryStore (graph storage)
      - MemoryRetriever (semantic search)
      - ConsolidationEngine (duplicate merge, contradiction resolution, pattern extraction)
    """

    def __init__(self, store: MemoryStore, retriever: MemoryRetriever):
        self.store = store
        self.retriever = retriever
        self.embedder = EmbeddingService()

        # NEW: Memory Consolidation Organ
        self.consolidation = ConsolidationEngine(
            store=self.store,
            embedder=self.embedder,
        )

    # ----------------------------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------------------------

    def write_memory(self, content: str, type: str = "fact") -> Dict[str, Any]:
        trace = {
            "content": content,
            "type": type,
        }

        # ConsolidationEngine handles graph storage
        result = self.consolidation.consolidate([trace])

        # ALSO write to vector store for retrieval
        embedding = self.embedder.embed(content)
        record = MemoryRecord(
            id=str(uuid.uuid4()),
            content=content,
            metadata={"type": type},
            embedding=embedding.tolist() if hasattr(embedding, "tolist") else embedding,
        )
        self.store.add(record)

        return result


    def consolidate_batch(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolidate a batch of traces (episodic logs, skill traces, etc.)
        """
        return self.consolidation.consolidate(traces)

    def retrieve(self, query: str) -> List[str]:
        """
        Returns a list of memory snippets relevant to the query.
        """
        return self.retriever.retrieve(query)

    def get_graph(self):
        """
        Returns a snapshot of the consolidated memory graph.
        """
        return self.store.graph_snapshot()
