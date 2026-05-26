from brain.c2.meta_types import MetaSignal, MetaDecision


class MetaController:
    """
    C6 Meta-Controller.

    Regulates:
    - planning depth
    - reasoning mode
    - cautious vs aggressive planning
    """

    def __init__(self):
        self.default_depth = 1
        self.max_depth = 4
        self.min_depth = 1
        self.current_depth = 1

    def observe_cycle(self, signal: MetaSignal) -> MetaDecision:
        # 1. Error → cautious mode
        if signal.error:
            self.current_depth = max(self.min_depth, self.current_depth - 1)
            return MetaDecision(
                action="switch_mode",
                value="cautious",
                reason="Execution error detected",
                notes={"depth": self.current_depth},
            )

        plan = signal.planner_trace[-1]
        step_count = len(plan.steps)

        # 2. Too long → reduce depth
        if step_count > 6:
            self.current_depth = max(self.min_depth, self.current_depth - 1)
            return MetaDecision(
                action="reduce_depth",
                value=self.current_depth,
                reason="Plan too long",
                notes={"steps": step_count},
            )

        # 3. Too shallow → increase depth
        if step_count <= 1:
            self.current_depth = min(self.max_depth, self.current_depth + 1)
            return MetaDecision(
                action="increase_depth",
                value=self.current_depth,
                reason="Plan too shallow",
                notes={"steps": step_count},
            )

        # 4. Memory-sensitive mode
        if plan.meta.get("memory_hits", 0) > 0:
            return MetaDecision(
                action="maintain_mode",
                value="memory_sensitive",
                reason="Memory context detected",
                notes={"memory_hits": plan.meta["memory_hits"]},
            )

        # 5. Stable
        return MetaDecision(
            action="noop",
            value=self.current_depth,
            reason="Stable cycle",
        )
