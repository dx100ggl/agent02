# tests/ch8/conftest.py

import pytest

from brain.c3.memory.store import InMemoryStore
from brain.c3.memory.retriever import MemoryRetriever
from brain.c3.memory.memory_service import MemoryService

from brain.c4.memory_layer import C4SemanticLayer
from brain.c5.memory_layer import C5BeliefLayer


@pytest.fixture
def memory_stack():
    """
    Shared CH8 memory stack:
    - C3 store + retriever
    - C4 semantic layer (auto‑creates cluster store)
    - C5 belief layer
    - MemoryService with C4 + C5
    """
    store = InMemoryStore()
    retriever = MemoryRetriever(store)

    # Your actual C4 constructor only takes the C3 store
    c4 = C4SemanticLayer(store)

    # Your C5 layer takes store + retriever
    c5 = C5BeliefLayer(store)

    memory = MemoryService(
        store,
        retriever,
        c4_layer=c4,
        c5_layer=c5,
    )

    return memory
