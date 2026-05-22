from brain.c1.state import State
from brain.c2.planner.adaptive_planner import AdaptivePlanner
from brain.c2.router.dynamic_router import DynamicRouter
from brain.c2.executor.executor import Executor

from brain.c3.memory.store import MemoryStore
from brain.c4.tools.registry import ToolRegistry

from brain.c5.reflection_engine import ReflectionEngineV1
from brain.c5.integration.c2_hooks import apply_directives_to_planner
from brain.c5.integration.c3_hooks import apply_memory_updates
from brain.c5.integration.c4_hooks import apply_skill_metadata_updates


MAX_STEPS = 5


class Orchestrator:
    """
    Brain-24 Orchestrator (C2.5)

    Semantics (aligned with tests):
    - Planner is called each iteration.
    - Only the FIRST step of the plan is executed.
    - Single-step plan => treat result as final.
    - Stop on {"final": True} or {"error": True}.
    - Enforce MAX_STEPS with an error.
    - Append each result to state.history as:
        {"step": step, ...flattened result...}
    - Set state.done = True on any termination.
    """

    def __init__(self, router=None, planner=None, executor=None, tools=None, memory=None):
        self.state = State()

        self.memory = memory if memory is not None else MemoryStore()
        self.tools = tools if tools is not None else ToolRegistry()

        self.planner = planner if planner is not None else AdaptivePlanner()
        self.router = router if router is not None else DynamicRouter()
        self.executor = executor if executor is not None else Executor()

        self.reflection = ReflectionEngineV1()

    def run(self, state):
        self.state = state

        planner_trace = []
        executor_trace = []
        final_output = None
        error = None
        steps = 0

        while True:
            # --- 1. Planning ---
            plan = self.planner.plan(state)
            planner_trace.append(plan)

            if not plan:
                state.done = True
                final_output = {"error": True, "message": "empty plan"}
                break

            # Single-step termination rule: execute only the first step
            step = plan[0]

            # --- 2. Routing (mode detection only) ---
            _route_mode = self.router.route(state)

            # --- 3. Execution ---
            result = self.executor.execute(step, state)

            executor_trace.append({"step": step, "result": result})

            # History entry: include step + flattened result
            history_entry = {"step": step}
            if isinstance(result, dict):
                history_entry.update(result)
            else:
                history_entry["result"] = result
            state.history.append(history_entry)

            final_output = result
            steps += 1

            # Stop on explicit final
            if isinstance(result, dict) and result.get("final"):
                state.done = True
                break

            # Stop on explicit error
            if isinstance(result, dict) and result.get("error"):
                state.done = True
                error = result
                break

            # Single-step plan => treat as final
            if len(plan) == 1:
                state.done = True
                break

            # Max depth guard
            if steps >= MAX_STEPS:
                final_output = {
                    "error": True,
                    "message": "Max cognitive depth exceeded",
                }
                error = final_output
                state.history.append(
                    {"step": {"action": "guard"}, "error": True, "message": final_output["message"]}
                )
                state.done = True
                break

        # --- 4. Reflection (C5) ---
        from brain.c5.reflection_types import ReflectionInput

        reflection_input = ReflectionInput(
            task_id=state.task_id,
            planner_trace=planner_trace,
            executor_trace=executor_trace,
            final_output=final_output,
            error=error,
        )

        reflection_output = self.reflection.reflect(reflection_input)

        # --- 5. Apply directives ---
        apply_directives_to_planner(self.planner, reflection_output.directives)
        apply_memory_updates(self.memory, reflection_output.memory_updates)
        apply_skill_metadata_updates(self.tools, reflection_output.directives)

        # --- 6. Return final output ---
        return final_output
