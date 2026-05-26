from typing import Optional, List, Dict, Any

from brain.c1.state import State
from brain.c1.planner.adaptive_planner import AdaptivePlanner
from brain.c1.planner.plan import Plan
from brain.c2.router.dynamic_router import DynamicRouter
from brain.c2.executor.executor import Executor

from brain.c3.memory.store import MemoryStore
from brain.c4.tools.registry import ToolRegistry

from brain.c5.reflection_engine import ReflectionEngineV1
from brain.c5.integration.c2_hooks import apply_directives_to_planner
from brain.c5.integration.c3_hooks import apply_memory_updates
from brain.c5.integration.c4_hooks import apply_skill_metadata_updates
from brain.c5.trace_logger import TraceLogger

from brain.c2.meta_controller import MetaController
from brain.c2.meta_planner import C2MetaPlanner
from brain.c2.evaluator import C2Evaluator
from brain.c2.repair_planner import C2RepairPlanner


class Orchestrator:
    """
    Brain-24 Orchestrator (C2.5 / C6 integrated).
    """

    def __init__(
        self,
        router: Optional[DynamicRouter] = None,
        planner: Optional[AdaptivePlanner] = None,
        executor: Optional[Executor] = None,
        tools: Optional[ToolRegistry] = None,
        memory: Optional[MemoryStore] = None,
        meta_controller: Optional[MetaController] = None,
    ):
        self.state = State()

        self.memory = memory if memory is not None else MemoryStore()
        self.tools = tools if tools is not None else ToolRegistry()

        # Ensure a default LLM exists
        if "llm" not in self.tools.tools:
            class DefaultLLM:
                def run(self, payload):
                    text = payload.get("text") or payload.get("prompt") or ""
                    return {"text": f"LLM:{text}"}

            self.tools.register("llm", DefaultLLM())
            self.tools.default_llm = "llm"


        self.planner = planner if planner is not None else AdaptivePlanner(tools=self.tools)
        self.router = router if router is not None else DynamicRouter()
        self.executor = executor if executor is not None else Executor(
            tools=self.tools,
            memory=self.memory,
        )

        self.meta_planner = C2MetaPlanner()
        self.plan_evaluator = C2Evaluator()
        self.repair_planner = C2RepairPlanner()

        self.reflection = ReflectionEngineV1()
        self.meta_controller = meta_controller if meta_controller is not None else MetaController()

    def run(self, state: State):
        self.state = state

        planner_trace: List[Any] = []
        executor_trace: List[Dict[str, Any]] = []
        final_output: Any = None
        error: Optional[Dict[str, Any]] = None

        # 1. Memory retrieval
        memory_results = self.memory.search(state.user_input)
        state.memory_results = memory_results

        # 2. C2 meta-planning
        directive = self.meta_planner.create_directive(state.user_input)

        # 3. C1 planning (tool-aware, memory-guided)
        plan: Plan = self.planner.create_plan(
            user_input=state.user_input,
            directive=directive,
            memory_results=memory_results,
        )

        plan.log(
            "c2_meta_planning",
            {
                "mode": directive.mode.value,
                "schema": directive.schema,
            },
        )
        TraceLogger.log_planner(state, plan)
        planner_trace.append(plan)

        # 4. C2 evaluation
        eval_result = self.plan_evaluator.evaluate_plan(plan)
        plan.log("c2_evaluation", eval_result)

        if not eval_result.get("ok", True):
            repaired = self.repair_planner.repair(plan)
            plan.log("c2_repair", repaired)

        # 5. Routing
        route_mode = self.router.route(state)
        TraceLogger.log_router(state, route_mode)

        # 6. Execution
        plan.log("execution_start", {"steps": len(plan.steps)})
        final_output = self.executor.execute_plan(plan, state)
        plan.log("execution_end", {"final_output": final_output})

        executor_trace.append({"plan": plan, "final_output": final_output})
        TraceLogger.log_executor(state, {"plan": "plan_v2"}, {"final_output": final_output})

        # 7. History
        state.history.append(
            {
                "plan_meta": plan.meta,
                "route_mode": route_mode,
                "final_output": final_output,
            }
        )
        state.done = True

        # 8. Reflection
        from brain.c5.reflection_types import ReflectionInput

        reflection_input = ReflectionInput(
            task_id=state.task_id,
            planner_trace=planner_trace,
            executor_trace=executor_trace,
            final_output=final_output,
            error=error,
            plan_trace=plan.trace,
        )

        reflection_output = self.reflection.reflect(reflection_input)
        TraceLogger.log_reflection(state, reflection_output)

        # 9. Apply reflection outputs
        apply_directives_to_planner(self.planner, reflection_output.directives)
        apply_memory_updates(self.memory, reflection_output.memory_updates)
        apply_skill_metadata_updates(self.tools, reflection_output.directives)
        TraceLogger.log_final(state, final_output)

        # 10. Meta-cognition (C6)
        if self.meta_controller is not None:
            from brain.c2.meta_types import MetaSignal

            trace_log = getattr(state, "trace_log", [])

            signal = MetaSignal(
                user_input=state.user_input,
                planner_trace=planner_trace,
                executor_trace=executor_trace,
                final_output=final_output,
                error=error,
                trace_log=trace_log,
                context={"phase": "post_execution"},
            )

            meta_decision = self.meta_controller.observe_cycle(signal)

            if meta_decision.action == "increase_depth":
                self.planner.set_preference("planning_depth", meta_decision.value)
            elif meta_decision.action == "reduce_depth":
                self.planner.set_preference("planning_depth", meta_decision.value)
            elif meta_decision.action == "switch_mode":
                self.planner.meta_mode = meta_decision.value

            TraceLogger.log(
                state,
                f"[meta] decision={meta_decision}",
            )

        # 11. Optional plan visualization
        if getattr(state, "debug_visualize_plan", False):
            from brain.c2.plan_visualizer import PlanVisualizer
            state.plan_visualization = PlanVisualizer.visualize(plan)

        return final_output
