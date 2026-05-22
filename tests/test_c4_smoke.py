from brain.build import run_brain, build_brain
from brain.state import BrainState
from brain.tools.registry import ToolRegistry
from brain.memory.store import LocalMemoryStore


def test_c4_smoke_llm_mode():
    """Basic LLM-only path."""
    result = run_brain("hello world")
    assert isinstance(result, dict)
    assert "thought" in result or "LLM" in str(result)


def test_c4_smoke_tool_mode():
    """Router should detect 'search' and trigger tool mode."""
    result = run_brain("please search for apples")
    assert isinstance(result, dict)
    assert "results" in result or "item" in str(result)


def test_c4_smoke_memory_write_and_query():
    """Memory store should accept writes and return matches."""
    store = LocalMemoryStore()
    store.put({"text": "Da likes adaptive brains"})
    store.put({"text": "C4 is adaptive cognition"})
    store.put({"text": "Tools and memory are integrated"})

    results = store.query("adaptive")
    assert len(results) >= 1
    assert "adaptive" in results[0]["text"].lower()


def test_c4_smoke_orchestrator_loop_runs():
    """Full orchestrator loop should run without errors."""
    brain = build_brain()
    state = BrainState("hello")
    result = brain.run(state)

    assert isinstance(result, dict)
    assert len(state.history) > 0
    assert state.done is True


def test_c4_smoke_router_modes():
    """Router should switch modes based on input."""
    from brain.router.dynamic_router import DynamicRouter
    from brain.state import BrainState

    router = DynamicRouter()

    assert router.route(BrainState("search for cats")) == "tool_mode"
    assert router.route(BrainState("hello")) == "llm_mode"


def test_c4_smoke_planner_adaptive():
    """Planner should revise plan on error."""
    from brain.planner.adaptive_planner import AdaptivePlanner
    from brain.state import BrainState

    planner = AdaptivePlanner()
    state = BrainState("hello")

    # initial plan
    plan1 = planner.plan(state)
    assert plan1[0]["action"] == "think"

    # simulate an error in history
    state.history.append({"error": True})
    plan2 = planner.plan(state)
    assert plan2[0]["action"] == "use_tool"


def test_c4_planner_escalates_after_retries():
    from brain.planner.adaptive_planner import AdaptivePlanner
    from brain.state import BrainState

    planner = AdaptivePlanner()
    state = BrainState("something hard")

    # simulate two failed attempts
    state.history.append({"step": {"action": "think"}, "error": True, "retries": 0})
    plan1 = planner.plan(state)
    assert plan1[0]["action"] == "think"
    assert plan1[0].get("retries") == 1

    state.history.append({"step": plan1[0], "error": True, "retries": 1})
    plan2 = planner.plan(state)
    assert plan2[0]["action"] == "think"
    assert plan2[0].get("retries") == 2

    # third failure → escalate to tool
    state.history.append({"step": plan2[0], "error": True, "retries": 2})
    plan3 = planner.plan(state)
    assert plan3[0]["action"] == "use_tool"
    assert plan3[0]["tool"] == "search"
