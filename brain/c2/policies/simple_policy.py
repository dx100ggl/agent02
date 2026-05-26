from __future__ import annotations

from typing import Optional

from brain.c2.meta_types import MetaConfig, MetaSignal, MetaDecision
from brain.c5.heuristics.efficiency_rules import estimate_efficiency_risk
from brain.c5.heuristics.hallucination_rules import estimate_hallucination_risk

class SimpleMetaPolicy:
    """
    A minimal, heuristic-driven meta policy.

    It reads C5 heuristics and turns them into high-level meta decisions.
    """

    def __init__(self, config: Optional[MetaConfig] = None) -> None:
        self._config = config or MetaConfig()

    def evaluate(self, signal: MetaSignal) -> MetaDecision:
        # Use C5 heuristics if enabled.
        halluc_risk = (
            signal.hallucination_risk
            if signal.hallucination_risk
            else estimate_hallucination_risk(signal.raw_trace)
        )
        eff_risk = (
            signal.efficiency_risk
            if signal.efficiency_risk
            else estimate_efficiency_risk(signal.raw_trace)
        )

        decision = MetaDecision(
            should_reflect=False,
            reflection_reason=None,
            increase_planning_depth=False,
            reduce_tool_calls=False,
            force_memory_write=False,
            hints={},
        )

        if self._config.enable_reflection and halluc_risk > 0.6:
            decision.should_reflect = True
            decision.reflection_reason = "High hallucination risk"
            decision.increase_planning_depth = True
            decision.force_memory_write = True

        if self._config.enable_heuristics and eff_risk > 0.6:
            decision.reduce_tool_calls = True
            decision.hints["efficiency_warning"] = True

        decision.hints["hallucination_risk"] = halluc_risk
        decision.hints["efficiency_risk"] = eff_risk

        return decision
