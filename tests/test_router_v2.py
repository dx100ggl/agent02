from brain.c2.router.dynamic_router import DynamicRouter
from brain.c1.state import BrainState


def test_router_routes_search_to_tool():
    router = DynamicRouter()
    state = BrainState("please search for apples")
    mode = router.route_raw(state)
    assert mode == "tool"


def test_router_routes_chat_to_llm():
    router = DynamicRouter()
    state = BrainState("hello world")
    mode = router.route_raw(state)
    assert mode == "llm"


def test_router_intent_classifier_basic():
    router = DynamicRouter()

    assert router._classify_intent("please search for cats") == "search"
    assert router._classify_intent("can we talk about something") == "chat"
    assert router._classify_intent("") == "chat"
