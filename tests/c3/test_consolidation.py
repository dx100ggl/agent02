# tests/c3/test_consolidation.py

import numpy as np
import pytest

from brain.c3.memory.store import InMemoryStore
from brain.c3.memory.retriever import MemoryRetriever
from brain.c3.memory.embeddings import EmbeddingService
from brain.c3.memory.consolidation.consolidation_engine import ConsolidationEngine


# ----------------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------------

class FakeEmbeddingService(EmbeddingService):
    """
    Deterministic embeddings for testing.
    Maps content strings to fixed vectors.
    """

    def embed(self, text: str) -> np.ndarray:
        # Simple deterministic embedding: hash → vector
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
def engine(store, embedder):
    return ConsolidationEngine(
        store=store,
        embedder=embedder,
        duplicate_threshold=0.95,        # strict enough to avoid coffee merging
        strong_duplicate_threshold=0.98, # keep strong duplicates very tight
    )

# ----------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------

def test_create_new_node(engine, store):
    trace = {"content": "User likes quiet environments", "type": "preference"}

    result = engine.consolidate([trace])

    graph = result["graph"]
    changelog = result["changelog"]

    assert len(graph["nodes"]) == 1
    assert "[CREATE]" in changelog[0]


def test_strong_duplicate_merge(engine, store):
    trace1 = {"content": "User likes quiet environments", "type": "preference"}
    trace2 = {"content": "User likes quiet environments", "type": "preference"}

    engine.consolidate([trace1])
    result = engine.consolidate([trace2])

    graph = result["graph"]
    changelog = result["changelog"]

    assert len(graph["nodes"]) == 1
    assert any("[MERGE]" in entry for entry in changelog)


def test_weak_duplicate_merge(engine, store):
    trace1 = {"content": "User likes quiet environments", "type": "preference"}
    trace2 = {"content": "User prefers quiet places", "type": "preference"}

    engine.consolidate([trace1])
    result = engine.consolidate([trace2])

    graph = result["graph"]
    changelog = result["changelog"]

    # weak duplicate → semantic_match() returns True → merge
    assert len(graph["nodes"]) == 1
    assert any("[MERGE]" in entry for entry in changelog)


def test_batch_consolidation(engine, store):
    traces = [
        {"content": "User likes quiet environments", "type": "preference"},
        {"content": "User prefers quiet places", "type": "preference"},
        {"content": "User enjoys silence while working", "type": "preference"},
    ]

    result = engine.consolidate(traces)

    graph = result["graph"]

    # All three should merge into one node
    assert len(graph["nodes"]) == 1


def test_graph_integrity_after_multiple_operations(engine, store):
    traces = [
        {"content": "User likes quiet environments", "type": "preference"},
        {"content": "User likes quiet environments", "type": "preference"},
        {"content": "User enjoys coffee", "type": "preference"},
    ]

    engine.consolidate([traces[0]])
    engine.consolidate([traces[1]])
    result = engine.consolidate([traces[2]])

    graph = result["graph"]

    # Should have 2 nodes: quiet preference + coffee preference
    assert len(graph["nodes"]) == 2


def test_changelog_entries(engine, store):
    trace = {"content": "User likes quiet environments", "type": "preference"}

    result = engine.consolidate([trace])

    assert len(result["changelog"]) >= 1
    assert "[CREATE]" in result["changelog"][0]
