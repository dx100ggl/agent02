from brain.c2.meta_controller import MetaController
from brain.c2.meta_types import MetaSignal

def test_meta_controller_basic_decision():
    mc = MetaController()
    fake_plan = type("P", (), {"steps": [1]})
    signal = MetaSignal(
        user_input="hi",
        planner_trace=[fake_plan],
        executor_trace=[],
        final_output="ok",
        error=None,
        trace_log=[],
    )
    decision = mc.observe_cycle(signal)
    assert decision.action in ("increase_depth", "reduce_depth", "noop", "maintain_mode", "switch_mode")
