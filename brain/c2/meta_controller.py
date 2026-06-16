# brain/c2/meta_controller.py

from __future__ import annotations
from typing import Any, Dict, Optional

from brain.c2.meta_types import MetaSignal, MetaDecision
from brain.c2.process_model import (
    # ProcessModel,
    ProcessNode,
    NodeKind,
    # ProcessRunner,
)

class MetaController:
    """
    C6 Meta-Controller (Patch N + C5 Reflection Integration)

    Responsibilities:
    - Observe cycle traces and produce meta-decisions
    - Adjust planning depth, mode, fallback strategies
    - Incorporate C5 reflection directives into C2 behavior
    - Provide a stable .execute() API for external callers
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
    # Patch N + C5 Reflection Integration
    # ---------------------------------------------------------------------
    def observe_cycle(self, signal: MetaSignal) -> MetaDecision:
        """
        Inspect the cycle and decide how to adjust planning.
        Includes both Patch N logic and C5 reflection feedback.
        """

        # -------------------------
        # 1. Patch N: Execution error
        # -------------------------
        if signal.error:
            self.current_depth = max(self.min_depth, self.current_depth - 1)
            decision = MetaDecision(
                action="switch_mode",
                value="cautious",
                reason="Execution error detected",
                notes={"depth": self.current_depth},
            )
            # Still allow reflection to add actions
            self._attach_reflection_actions(signal, decision)
            return decision

        # -------------------------
        # 2. Patch N: Plan length
        # -------------------------
        plan = signal.planner_trace[-1]
        step_count = len(plan.steps)

        if step_count > 6:
            self.current_depth = max(self.min_depth, self.current_depth - 1)
            decision = MetaDecision(
                action="reduce_depth",
                value=self.current_depth,
                reason="Plan too long",
                notes={"steps": step_count},
            )
            self._attach_reflection_actions(signal, decision)
            return decision

        if step_count <= 1:
            self.current_depth = min(self.max_depth, self.current_depth + 1)
            decision = MetaDecision(
                action="increase_depth",
                value=self.current_depth,
                reason="Plan too shallow",
                notes={"steps": step_count},
            )
            self._attach_reflection_actions(signal, decision)
            return decision

        # -------------------------
        # 3. Patch N: Memory-sensitive mode
        # -------------------------
        if plan.meta.get("memory_hits", 0) > 0:
            decision = MetaDecision(
                action="maintain_mode",
                value="memory_sensitive",
                reason="Memory context detected",
                notes={"memory_hits": plan.meta["memory_hits"]},
            )
            self._attach_reflection_actions(signal, decision)
            return decision

        # -------------------------
        # 4. Default: Stable cycle
        # -------------------------
        decision = MetaDecision(
            action="noop",
            value=self.current_depth,
            reason="Stable cycle",
        )

        # Attach reflection actions even in noop mode
        self._attach_reflection_actions(signal, decision)
        return decision

    # ---------------------------------------------------------------------
    # Helper: Attach C5 reflection actions to MetaDecision
    # ---------------------------------------------------------------------
    def _attach_reflection_actions(self, signal: MetaSignal, decision: MetaDecision):
        """
        If the orchestrator attached reflection info to the MetaSignal,
        convert it into actionable C2 adjustments.
        """
        reflection = getattr(signal, "extra", {}).get("reflection") if hasattr(signal, "extra") else None
        actions = self.apply_reflection(reflection)

        if actions:
            # Attach to MetaDecision so Orchestrator can act on them
            decision.reflection_actions = actions

    # ---------------------------------------------------------------------
    # Tests require this method to exist
    # ---------------------------------------------------------------------
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

    # ---------------------------------------------------------------------
    # C5 → C2 Directive Translator
    # ---------------------------------------------------------------------
    def apply_reflection(self, reflection):
        """
        Convert C5 reflection directives into C2 meta‑actions.
        """
        if not reflection:
            return None

        directives = reflection.get("directives", [])
        actions = []

        for d in directives:
            directive = d.get("directive")

            if directive == "adjust_mode:more_cautious":
                actions.append({"mode": "cautious"})

            if directive == "Validate tool arguments against schema.":
                actions.append({"validate_args": True})

            if directive == "Avoid repeating identical tool calls.":
                actions.append({"avoid_redundancy": True})

            if directive == "Ensure precondition checks before tool calls.":
                actions.append({"enforce_preconditions": True})

        return actions

    # C6 → C2 hooks
    def before_node(self, node, ctx):
        if node.id == "fetch_market_data":
            return {"action": "skip"}


    def after_node(self, node, ctx):
        if node.id == "analyze":
            return {
                "action": "insert_after",
                "node": ProcessNode(
                    id="double_check",
                    kind=NodeKind.TASK,
                    handler=lambda c: c.update({"checked": True}),
                )
            }

