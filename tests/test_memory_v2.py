from brain.c3.memory.embeddings import SimpleEmbedder
from brain.c3.memory.store import MemoryStore
from brain.c3.memory.retriever import MemoryRetriever
from brain.c1.state import BrainState


def test_embedder_is_deterministic():
    emb = SimpleEmbedder()

    v1 = emb.embed("hello world")
    v2 = emb.embed("hello world")
    v3 = emb.embed("different text")

    assert v1 == v2
    assert v1 != v3


def test_memory_store_retrieves_relevant_item():
    store = MemoryStore()
    store.add("I like apples", {"type": "preference"})
    store.add("The capital of France is Paris", {"type": "fact"})
    store.add("Bananas are yellow", {"type": "fact"})

    results = store.search("France capital", top_k=1)
    assert len(results) == 1
    assert "France" in results[0].text


def test_memory_retriever_filters_by_score():
    store = MemoryStore()
    store.add("Completely unrelated sentence about cats")
    store.add("Another random note about weather")

    retriever = MemoryRetriever(store=store, min_score=0.9)
    state = BrainState("quantum mechanics and black holes")

    results = retriever.retrieve(state, top_k=5)
    # With a high threshold and unrelated content, we expect no hits.
    assert results == []
