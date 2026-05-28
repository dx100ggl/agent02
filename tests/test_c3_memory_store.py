# tests/test_c3_memory_store.py

from brain.c3.memory.retriever import SimpleMemoryProvider
from brain.c3.memory.base import MemoryQuery


def test_memory_store_search():
    memory = SimpleMemoryProvider()

    memory.write("cats are cute", metadata={"tags": ["animal"]})
    memory.write("dogs are loyal", metadata={"tags": ["animal"]})

    query = MemoryQuery(query="cats", top_k=5)
    results = memory.search(query)

    assert len(results) >= 1
    assert any("cats" in r.record.content.lower() for r in results)
