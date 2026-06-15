# brain/c3/memory/memory_service.py

from __future__ import annotations
from typing import List, Dict, Any
import uuid

from brain.c3.memory.store import MemoryStore
from brain.c3.memory.retriever import MemoryRetriever
from brain.c3.memory.embeddings import EmbeddingService
from brain.c3.memory.consolidation.consolidation_engine import ConsolidationEngine
from brain.c3.memory.base import MemoryRecord

from brain.c4.memory_layer import C4SemanticLayer
from brain.c5.memory_layer import C5BeliefLayer


class MemoryService:
    """
    C3 Memory Service.
    Compatible with original test expectations:
        MemoryService(store, retriever)
    And extended for Chapter 8:
        optional C4 + C5 layers.
    """

    def __init__(
        self,
        store: MemoryStore,
        retriever: MemoryRetriever,
        c4_layer: C4SemanticLayer | None = None,
        c5_layer: C5BeliefLayer | None = None,
    ):
        # Required by tests
        self.store = store
        self.retriever = retriever

        # Derive embedder from retriever (tests rely on this)
        self.embedder: EmbeddingService = retriever.embedder

        # C3 consolidation engine
        self.engine = ConsolidationEngine(store=store, embedder=self.embedder)

        # Optional C4/C5 layers
        self.c4_layer = c4_layer
        self.c5_layer = c5_layer

    # ----------------------------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------------------------

    def write_memory(self, content: str, type: str = "fact") -> Dict[str, Any]:
        trace = {"content": content, "type": type}

        # C3 consolidation
        engine = getattr(self, "engine", None) or getattr(self, "consolidation")
        result = engine.consolidate([trace])

        # ALSO write to vector store for retrieval
        embedding = self.embedder.embed(content)
        record = MemoryRecord(
            id=str(uuid.uuid4()),
            content=content,
            metadata={"type": type},
            embedding=embedding.tolist() if hasattr(embedding, "tolist") else embedding,
        )
        self.store.add(record)

        # Drive higher layers
        if getattr(self, "c4_layer", None) is not None:
            self.c4_layer.rebuild_clusters()

        if getattr(self, "c5_layer", None) is not None:
            self.c5_layer.rebuild_beliefs()


        return result

    def consolidate_batch(self, traces: list[dict]) -> dict:
        engine = getattr(self, "engine", None) or getattr(self, "consolidation")
        result = engine.consolidate(traces)


        if getattr(self, "c4_layer", None) is not None:
            self.c4_layer.rebuild_clusters()

        if getattr(self, "c5_layer", None) is not None:
            self.c5_layer.rebuild_beliefs()


        return result

    def retrieve(self, query: str) -> List[str]:
        return self.retriever.retrieve(query)

    def get_graph(self):
        return self.store.graph_snapshot()

    def get_clusters(self):
        if self.c4_layer is None:
            return []
        return self.c4_layer.get_clusters()

    def get_beliefs(self):
        if self.c5_layer is None:
            return []
        return self.c5_layer.get_beliefs()
