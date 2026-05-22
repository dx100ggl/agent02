from brain.planner.adaptive_planner import AdaptivePlanner
from brain.state import BrainState


def test_planner_uses_memory_when_strong_hit_present():
    """
    If strong memory results are attached to the state,
    planner v3.5 should choose a think step that uses memory.
    """
    planner = AdaptivePlanner()
    state = BrainState("Who likes adaptive brains?")

    # Simulate memory retrieval attaching results to the state.
    state.memory_results = [
        {"text": "Da likes adaptive brains", "score": 0.9},
    ]

    plan = planner.plan(state)
    assert isinstance(plan, list)
    assert plan[0]["action"] == "think"
    assert plan[0].get("use_memory") is True
