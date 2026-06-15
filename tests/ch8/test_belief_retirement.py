# tests/ch8/test_belief_retirement.py

from brain.c2.orchestrator import Orchestrator
from brain.c1.state import State

from brain.c3.memory.store import InMemoryStore
from brain.c3.memory.retriever import MemoryRetriever
from brain.c3.memory.memory_service import MemoryService

from brain.c4.clustering.cluster_store import InMemoryClusterStore
from brain.c4.clustering.clusterer import SimpleKeywordClusterer
from brain.c4.memory_layer import C4SemanticLayer

from brain.c5.memory_layer import C5BeliefLayer


def test_weak_beliefs_are_retired():
    store = InMemoryStore()
    retriever = MemoryRetriever(store)

    cluster_store = InMemoryClusterStore()
    clusterer = SimpleKeywordClusterer(store, cluster_store)

    c4 = C4SemanticLayer(store, clusterer, cluster_store)
    c5 = C5BeliefLayer(store)

    memory = MemoryService(store, retriever, c4_layer=c4, c5_layer=c5)
    orch = Orchestrator(memory=memory)

    # Create a belief that should be retired
    b = c5.belief_store.create(
        kind="preference",
        metadata={"tags": ["detailed"]},
        strength=0.01,
        cluster_id="x"
    )
    c5.belief_store.add(b)

    state = State(task_id="t1", user_input="research META")
    orch.run(state)

    assert c5.belief_store.get(b.id) is None
