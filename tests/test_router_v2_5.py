from brain.c2.router.dynamic_router import DynamicRouter
from brain.c3.memory.store import MemoryStore
from brain.c1.state import BrainState


def test_router_memory_first_when_relevant():
    store = MemoryStore()
    store.add("Da likes adaptive brains")
    router = DynamicRouter(memory=store)

    state = BrainState("adaptive brains")
    mode = router.route_raw(state)

    assert mode == "memory"


def test_router_falls_back_to_tool_for_search():
    router = DynamicRouter()
    state = BrainState("please search for apples")
    assert router.route_raw(state) == "tool"


def test_router_defaults_to_llm():
    router = DynamicRouter()
    state = BrainState("hello world")
    assert router.route_raw(state) == "llm"
