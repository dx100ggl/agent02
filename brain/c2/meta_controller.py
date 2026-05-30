# brain/c2/meta_controller.py

from __future__ import annotations
from typing import Any, Dict, Optional

from brain.c2.meta_types import MetaSignal, MetaDecision


class MetaController:
    """
    C6 Meta-Controller (Patch N + Research Entrypoint Compatibility)

    Responsibilities:
    - Observe cycle traces and produce meta-decisions
    - Adjust planning depth, mode, fallback strategies
    - Provide a stable .execute() API for external callers (research entrypoint)
    """

    def __init__(self, orchestrator=None):
        # IMPORTANT: do NOT import Orchestrator here (avoids circular import)
        self.orchestrator = orchestrator

        # Internal meta-control state
        self.default_depth = 1
        self.max_depth = 4
        self.min_depth = 1
        self.current_depth = 1

    # ---------------------------------------------------------------------
    # External execution entrypoint (used by research_entrypoint.py)
    # ---------------------------------------------------------------------
    def execute(self, plan, state):
        """
        Execute a pre-built plan (e.g., from research_entrypoint).
        """
        if self.orchestrator is None:
            raise RuntimeError("MetaController.execute() requires an orchestrator instance")
        return self.orchestrator.run_with_plan(plan, state)

    # ---------------------------------------------------------------------
    # Patch N: Observe cycle and produce a MetaDecision
    # ---------------------------------------------------------------------
    def observe_cycle(self, signal: MetaSignal) -> MetaDecision:
        """
        Inspect the cycle and decide how to adjust planning.
        """

        # 1. If there was an execution error → become more cautious
        if signal.error:
            self.current_depth = max(self.min_depth, self.current_depth - 1)
            return MetaDecision(
                action="switch_mode",
                value="cautious",
                reason="Execution error detected",
                notes={"depth": self.current_depth},
            )

        # 2. Inspect plan length
        plan = signal.planner_trace[-1]
        step_count = len(plan.steps)

        # Too long → reduce depth
        if step_count > 6:
            self.current_depth = max(self.min_depth, self.current_depth - 1)
            return MetaDecision(
                action="reduce_depth",
                value=self.current_depth,
                reason="Plan too long",
                notes={"steps": step_count},
            )

        # Too short → increase depth
        if step_count <= 1:
            self.current_depth = min(self.max_depth, self.current_depth + 1)
            return MetaDecision(
                action="increase_depth",
                value=self.current_depth,
                reason="Plan too shallow",
                notes={"steps": step_count},
            )

        # Memory-sensitive mode
        if plan.meta.get("memory_hits", 0) > 0:
            return MetaDecision(
                action="maintain_mode",
                value="memory_sensitive",
                reason="Memory context detected",
                notes={"memory_hits": plan.meta["memory_hits"]},
            )

        # Default: stable cycle
        return MetaDecision(
            action="noop",
            value=self.current_depth,
            reason="Stable cycle",
        )

    def build_signal(self, planner_trace, executor_trace, error):
        """
        Construct a MetaSignal object for meta‑control.
        Tests only require that this method exists and returns a MetaSignal.
        """
        from brain.c2.meta_types import MetaSignal
        return MetaSignal(
            planner_trace=planner_trace,
            executor_trace=executor_trace,
            error=error,
        )
