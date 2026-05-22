from brain.router.dynamic_router import DynamicRouter
from brain.planner.adaptive_planner import AdaptivePlanner
from brain.executor.executor import Executor
from brain.state import BrainState


class Orchestrator:
    """
    Orchestrator v2 (corrected):
    - Executes multi-step plans.
    - Single-step plans are final (LLM-only path).
    - Tool steps are final.
    - Multi-step plans loop.
    - MAX_STEPS protects against runaway loops.
    """

    MAX_STEPS = 12

    def __init__(self, router: DynamicRouter, planner: AdaptivePlanner, executor: Executor):
        self.router = router
        self.planner = planner
        self.executor = executor

    def run(self, state: BrainState):
        steps_executed = 0

        while not state.done:

            # ---------------------------------------------------------
            # 1. Max depth protection
            # ---------------------------------------------------------
            if steps_executed >= self.MAX_STEPS:
                state.done = True
                return {"error": True, "message": "Max cognitive depth reached"}

            # ---------------------------------------------------------
            # 2. Router (not used yet, but kept for future expansion)
            # ---------------------------------------------------------
            mode = self.router.route(state)

            # ---------------------------------------------------------
            # 3. Planner produces plan
            # ---------------------------------------------------------
            plan = self.planner.plan(state)
            if not plan:
                state.done = True
                return {"error": True, "message": "Planner returned empty plan"}

            step = plan[0]

            # ---------------------------------------------------------
            # 4. Execute step
            # ---------------------------------------------------------
            result = self.executor.execute(step, state)

            # ---------------------------------------------------------
            # 5. Record history
            # ---------------------------------------------------------
            state.history.append({
                "step": step,
                "result": result,
                "error": result.get("error", False),
                "retries": step.get("retries", 0),
            })

            steps_executed += 1

            # ---------------------------------------------------------
            # 6. Explicit final signal
            # ---------------------------------------------------------
            if result.get("final"):
                state.done = True
                return result

            # ---------------------------------------------------------
            # 7. Tool steps are always final
            # ---------------------------------------------------------
            if step["action"] == "use_tool":
                state.done = True
                return result

            # ---------------------------------------------------------
            # 8. Single-step plans are final (LLM-only path)
            # ---------------------------------------------------------
            if len(plan) == 1:
                state.done = True
                return result

            # ---------------------------------------------------------
            # 9. Multi-step plans → continue loop
            # ---------------------------------------------------------
            # (Planner v2 currently only returns multi-step for tool-first)
            continue

        # Fallback
        return state.history[-1]["result"] if state.history else {}
