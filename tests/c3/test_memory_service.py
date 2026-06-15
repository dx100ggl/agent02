# tests/c3/test_memory_service.py

import pytest
import numpy as np

from brain.c3.memory.store import InMemoryStore
from brain.c3.memory.retriever import MemoryRetriever
from brain.c3.memory.memory_service import MemoryService
from brain.c3.memory.embeddings import EmbeddingService
from brain.c3.memory.consolidation.consolidation_engine import ConsolidationEngine


# ----------------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------------

class FakeEmbeddingService(EmbeddingService):
    """
    Deterministic embeddings for stable tests.
    """

    def embed(self, text: str) -> np.ndarray:
        h = abs(hash(text)) % 1000
        return np.array([h, h / 2, h / 3], dtype=float)


@pytest.fixture
def store():
    return InMemoryStore()


@pytest.fixture
def embedder():
    return FakeEmbeddingService()


@pytest.fixture
def retriever(store, embedder):
    return MemoryRetriever(store=store, embedder=embedder)


@pytest.fixture
def service(store, retriever, embedder, monkeypatch):
    """
    Patch MemoryService to use FakeEmbeddingService.
    """

    def fake_init(self, store, retriever, *args, **kwargs):
        self.store = store
        self.retriever = retriever
        self.embedder = embedder
        self.consolidation = ConsolidationEngine(
            store=store,
            embedder=embedder,
            duplicate_threshold=kwargs.get("duplicate_threshold", 0.88),
            strong_duplicate_threshold=kwargs.get("strong_duplicate_threshold", 0.93),
        )

    monkeypatch.setattr(MemoryService, "__init__", fake_init)

    return MemoryService(
        store=store,
        retriever=retriever,
        duplicate_threshold=0.95,
        strong_duplicate_threshold=0.98,
    )


# ----------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------

def test_write_memory_creates_node(service):
    result = service.write_memory("User likes quiet environments", type="preference")

    graph = result["graph"]
    changelog = result["changelog"]

    assert len(graph["nodes"]) == 1
    assert any("[CREATE]" in entry for entry in changelog)


def test_write_memory_merges_duplicates(service):
    service.write_memory("User likes quiet environments", type="preference")
    result = service.write_memory("User likes quiet environments", type="preference")

    graph = result["graph"]
    changelog = result["changelog"]

    assert len(graph["nodes"]) == 1
    assert any("[MERGE]" in entry for entry in changelog)


def test_consolidate_batch(service):
    traces = [
        {"content": "User likes quiet environments", "type": "preference"},
        {"content": "User prefers quiet places", "type": "preference"},
        {"content": "User enjoys silence while working", "type": "preference"},
    ]

    result = service.consolidate_batch(traces)
    graph = result["graph"]

    assert len(graph["nodes"]) == 1


def test_retrieve_still_works(service):
    service.write_memory("User likes quiet environments", type="preference")

    results = service.retrieve("quiet")

    assert isinstance(results, list)
    assert len(results) >= 1


def test_get_graph(service):
    service.write_memory("User likes quiet environments", type="preference")

    graph = service.get_graph()

    assert "nodes" in graph
    assert len(graph["nodes"]) == 1


def test_changelog_format(service):
    result = service.write_memory("User likes quiet environments", type="preference")

    changelog = result["changelog"]

    assert isinstance(changelog, list)
    assert any("[CREATE]" in entry for entry in changelog)
