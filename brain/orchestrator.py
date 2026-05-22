class Orchestrator:
    """
    Orchestrator v2.5 — memory-aware but fully backward-compatible.
    Executes planner steps through the executor, records history,
    respects final signals, and enforces MAX_STEPS.
    """

    MAX_STEPS = 10

    def __init__(self, router, planner, executor):
        self.router = router
        self.planner = planner
        self.executor = executor

    def run(self, state):
        steps = 0

        while not state.done:
            steps += 1
            if steps > self.MAX_STEPS:
                state.done = True
                return {"error": True, "message": "Max cognitive depth exceeded"}

            # 1. Router decides mode
            mode = self.router.route_raw(state)

            # 2. Memory-first mode
            if mode == "memory":
                memory_hits = self.executor.memory.retrieve(state, top_k=3)
                state.memory_context = memory_hits

            # 3. Planner decides next step
            plan = self.planner.plan(state)
            if not plan:
                return {"error": True, "message": "planner returned empty plan"}

            step = plan[0]

            # 4. Execute step via executor
            result = self.executor.execute(step, state)

            # 5. Record in history
            state.history.append({
                "step": step,
                "result": result,
                "error": result.get("error", False)
            })

            # 6. Final signal
            if isinstance(result, dict) and result.get("final"):
                state.done = True
                return result

            # 7. Single-step plan terminates immediately
            if len(plan) == 1:
                state.done = True
                return result

        return {"error": True, "message": "unexpected termination"}
