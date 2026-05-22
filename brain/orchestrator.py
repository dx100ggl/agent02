from brain.router.dynamic_router import DynamicRouter
from brain.planner.adaptive_planner import AdaptivePlanner
from brain.executor.executor import Executor
from brain.state import BrainState

class Orchestrator:
    def __init__(self, router: DynamicRouter, planner: AdaptivePlanner, executor: Executor):
        self.router = router
        self.planner = planner
        self.executor = executor

    def run(self, state: BrainState):
        while not state.done:
            mode = self.router.route(state)
            state.plan = self.planner.plan(state)

            if not state.plan:
                state.done = True
                break

            step = state.plan.pop(0)
            result = self.executor.execute(step, state)

            state.history.append({
                "step": step,
                "result": result,
                "error": result.get("error", False),
                "retries": step.get("retries", 0),
            })


            if len(state.history) > 5:
                state.done = True

        return state.history[-1]["result"]
