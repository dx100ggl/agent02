from brain.c6 import MetaController, MetaConfig, MetaSignal


def test_meta_controller_smoke():
    controller = MetaController(MetaConfig())

    signal = MetaSignal(
        user_input="test",
        planner_trace=[],
        executor_trace=[],
        final_output={"final": True},
        error=None,
        trace_log=[],
    )

    decision = controller.observe_cycle(signal)

    assert decision is not None
    assert decision.notes["has_final_error"] is False
