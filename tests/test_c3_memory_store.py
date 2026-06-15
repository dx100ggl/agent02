# tests/test_c3_memory_store.py

from brain.c3.memory.store import InMemoryStore
from brain.c3.memory.embeddings import EmbeddingService
from brain.c3.memory.retriever import MemoryRetriever
from brain.c3.memory.base import MemoryRecord, MemoryQuery


def test_memory_store_search():
    store = InMemoryStore()
    embedder = EmbeddingService()
    retriever = MemoryRetriever(store=store, embedder=embedder)

    # Write two memory records manually (this matches the new architecture)
    record1 = MemoryRecord(
        id="1",
        content="cats are cute",
        metadata={"tags": ["animal"]},
        embedding=embedder.embed("cats are cute"),
    )
    record2 = MemoryRecord(
        id="2",
        content="dogs are loyal",
        metadata={"tags": ["animal"]},
        embedding=embedder.embed("dogs are loyal"),
    )

    store.add(record1)
    store.add(record2)

    # Search using the new retriever API
    results = retriever.retrieve("cats")

    assert len(results) >= 1
    assert any("cats" in r.lower() for r in results)
