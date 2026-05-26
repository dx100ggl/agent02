from brain.c3.memory.store import MemoryStore

def test_memory_store_search():
    m = MemoryStore()
    m.add("cats are cute", tags=["animal"])
    m.add("dogs are loyal", tags=["animal"])

    results = m.search("cats")
    assert len(results) == 1
    assert "cats" in results[0].text.lower()
