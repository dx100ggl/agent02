from __future__ import annotations

from typing import Optional

from brain.c6.meta_types import MetaConfig, MetaSignal, MetaDecision


class MetaController:
    """
    C6 meta-cognition controller (Option C).

    - Observes traces after a turn.
    - Produces *suggestions* only (no hard control).
    - Can be wired in without changing existing behaviour.
    """

    def __init__(self, config: Optional[MetaConfig] = None) -> None:
        self._config = config or MetaConfig()

    def observe_cycle(self, signal: MetaSignal) -> MetaDecision:
        """
        Main entry point: called once per user turn.

        For now, we keep the policy deliberately simple and conservative.
        """
        decision = MetaDecision()

        # 1) If the last turn ended in error, suggest stronger reflection next time.
        if self._config.enable_reflection_hints and signal.error is not None:
            decision.should_reflect_next_turn = True
            decision.increase_planning_depth = True
            decision.reason = "Previous turn ended in error"
            decision.notes["error_seen"] = True

        # 2) If we used many steps, hint about efficiency.
        steps = len(signal.executor_trace)
        if (
            self._config.enable_efficiency_hints
            and steps >= self._config.max_steps_before_efficiency_warning
        ):
            decision.reduce_tool_calls = True
            if decision.reason is None:
                decision.reason = "High step count in previous turn"
            decision.notes["steps"] = steps

        # 3) Always attach some basic telemetry.
        decision.notes.setdefault("trace_log_length", len(signal.trace_log))
        decision.notes.setdefault("has_final_error", signal.error is not None)

        return decision
