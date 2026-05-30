# brain/c2/orchestrator.py

from __future__ import annotations

from typing import Optional, List, Dict, Any

from brain.c1.state import State
from brain.c1.planner.adaptive_planner import AdaptivePlanner
from brain.c1.planner.plan import Plan
from brain.c1.planner.intent_classifier import IntentClassifier

from brain.c2.router.dynamic_router import DynamicRouter
from brain.c2.executor.executor import Executor

from brain.c3.memory.base import MemoryProvider
from brain.c3.memory.retriever import SimpleMemoryProvider

from brain.c4.tools.registry import ToolRegistry

from brain.c5.reflection_engine import ReflectionEngine
from brain.c5.integration.c2_hooks import apply_directives_to_planner
from brain.c5.integration.c4_hooks import apply_skill_metadata_updates
from brain.c5.trace_logger import TraceLogger
from brain.c5.integration.c3_hooks import (
    C3MemoryHooks,
    MemoryHookContext,
)

from brain.c2.meta_controller import MetaController
from brain.c2.meta_planner import C2MetaPlanner
from brain.c2.evaluator import C2Evaluator
from brain.c2.repair_planner import C2RepairPlanner


class Orchestrator:
    """
    Brain-24 Orchestrator (C2.5 / C6 integrated, S4 version).

    - Uses C3MemoryHooks for read/write memory integration
    - Reflection results are persisted into C3
    """

    def __init__(
        self,
        router: Optional[DynamicRouter] = None,
        planner: Optional[AdaptivePlanner] = None,
        executor: Optional[Executor] = None,
        tools: Optional[ToolRegistry] = None,
        memory: Optional[MemoryProvider] = None,
        meta_controller: Optional[MetaController] = None,
        c3_hooks: Optional[C3MemoryHooks] = None,
    ):
        self.state = State()

        # --- C3 Memory ---
        self.memory: MemoryProvider = memory if memory is not None else SimpleMemoryProvider()

        # --- C4 Tools ---
        self.tools: ToolRegistry = tools if tools is not None else ToolRegistry([])

        # Ensure a default LLM exists
        if self.tools.default_llm not in self.tools.tools:
            class DefaultLLM:
                def run(self, payload):
                    text = payload.get("text") or payload.get("prompt") or ""
                    return {"text": f"LLM:{text}"}

            self.tools.register(self.tools.default_llm, DefaultLLM())

        # --- C1 / C2 core ---
        self.planner = planner if planner is not None else AdaptivePlanner()
        self.router = router if router is not None else DynamicRouter()
        self.executor = executor if executor is not None else Executor(
            tools=self.tools,
            memory=self.memory,
        )

        self.meta_planner = C2MetaPlanner()
        self.plan_evaluator = C2Evaluator()
        self.repair_planner = C2RepairPlanner()

        # --- C5 Reflection / C6 Meta ---
        self.reflection = ReflectionEngine()
        self.meta_controller = meta_controller if meta_controller is not None else MetaController()

        # --- C3 hooks (reflection + memory integration) ---
        self.c3_hooks: C3MemoryHooks = c3_hooks if c3_hooks is not None else C3MemoryHooks(self.memory)

        # ---------------------------------------------------------
        # C7 Skill Learning (injected by build.py)
        # ---------------------------------------------------------
        self.skill_router = getattr(self, "skill_router", None)
        self.skill_learner = getattr(self, "skill_learner", None)

    def run(self, state: State):
        self.state = state

        # Ensure meta exists (S4 / Brain-24)
        if not hasattr(state, "meta") or not isinstance(state.meta, dict):
            state.meta = {}

        planner_trace: List[Any] = []
        executor_trace: List[Dict[str, Any]] = []
        final_output: Any = None
        error: Optional[Dict[str, Any]] = None

        # 0. C7 Skill Routing (pre‑planning)
        # ---------------------------------------------------------
        if self.skill_router is not None:
            skill_result = self.skill_router.route(state.user_input)
            if skill_result is not None:
                # Skill executed successfully — return immediately
                state.history.append({
                    "skill_routed": True,
                    "final_output": skill_result,
                })
                state.done = True
                return skill_result

        # 0.5 Intent classification (C1, E2‑P3)
        # ---------------------------------------------------------
        if "intent" not in state.meta:
            classifier = IntentClassifier()
            llm_tool = self.tools.get(self.tools.default_llm)

            def _llm(prompt: str) -> str:
                raw = llm_tool.run({"text": prompt})
                if isinstance(raw, dict):
                    return str(raw.get("text") or raw.get("output") or raw.get("response") or "")
                return str(raw)

            intent_name = classifier.classify(_llm, state.user_input)
            state.meta["intent"] = intent_name

        # 1. Memory retrieval (C3 via hooks, planning phase)
        # ---------------------------------------------------------
        planning_ctx = MemoryHookContext(
            task_id=state.task_id,
            user_id=getattr(state, "user_id", None),
            phase="planning",
        )

        planning_memory_results = self.c3_hooks.retrieve_for_reflection(
            query=state.user_input,
            context=planning_ctx,
            top_k=5,
        )

        # 2. C2 meta-planning
        # ---------------------------------------------------------
        directive = self.meta_planner.create_directive(state.user_input)

        # 3. C1 planning (tool-aware, memory-guided)
        # ---------------------------------------------------------
        plan: Plan = self.planner.create_plan(
            user_input=state.user_input,
            directive=directive,
            memory_results=planning_memory_results,
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
        # ---------------------------------------------------------
        eval_result = self.plan_evaluator.evaluate_plan(plan)
        plan.log("c2_evaluation", eval_result)

        if not eval_result.get("ok", True):
            repaired = self.repair_planner.repair(plan)
            plan.log("c2_repair", repaired)

        # 5. Routing
        # ---------------------------------------------------------
        route_mode = self.router.route(state)
        TraceLogger.log_router(state, route_mode)

        # 6. Execution
        # ---------------------------------------------------------
        plan.log("execution_start", {"steps": len(plan.steps)})
        final_output = self.executor.execute_plan(plan, state)
        plan.log("execution_end", {"final_output": final_output})

        executor_trace.append({"plan": plan, "final_output": final_output})
        TraceLogger.log_executor(state, {"plan": "plan_v2"}, {"final_output": final_output})

        # 7. History
        # ---------------------------------------------------------
        state.history.append(
            {
                "plan_meta": plan.meta,
                "route_mode": route_mode,
                "final_output": final_output,
            }
        )
        state.done = True

        # ---------------------------------------------------------
        # 7.5 C7 Skill Learning (post‑execution)
        # ---------------------------------------------------------
        if self.skill_learner is not None:
            from brain.c2.skill_learning.skill_trace import SkillTrace, TraceStep

            def _step_action(s):
                # Prefer explicit action if present
                if hasattr(s, "action"):
                    return s.action
                # Fallbacks for typical PlanStep shapes
                if hasattr(s, "tool_name"):
                    return s.tool_name
                if hasattr(s, "name"):
                    return s.name
                # Last resort: class name
                return s.__class__.__name__

            def _step_params(s):
                if hasattr(s, "params"):
                    return s.params
                if hasattr(s, "tool_args"):
                    return s.tool_args
                return {}

            trace = SkillTrace(
                task_id=state.task_id,
                steps=[
                    TraceStep(
                        action=_step_action(step),
                        params=_step_params(step),
                        result=None,  # results not needed for learning
                    )
                    for step in plan.steps
                ],
            )

            # Let the learner observe this trace (may or may not yield a skill)
            self.skill_learner.learn_from_traces([trace])

        # 8. Reflection
        # ---------------------------------------------------------
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

        # 9. Apply reflection outputs + persist into C3 via hooks
        # ---------------------------------------------------------
        # 9.1 Apply directives to planner + tools
        apply_directives_to_planner(self.planner, reflection_output.directives)
        apply_skill_metadata_updates(self.tools, reflection_output.directives)

        # 9.2 Derive a reflection summary and store in C3
        summary_lines: List[str] = []

        if reflection_output.findings:
            summary_lines.append("Findings:")
            for f in reflection_output.findings:
                summary_lines.append(f"- [{f.category}] {f.description} (evidence: {f.evidence})")

        if reflection_output.directives:
            summary_lines.append("Directives:")
            for d in reflection_output.directives:
                summary_lines.append(f"- (priority={d.priority}) {d.directive}")

        if not summary_lines:
            summary_lines.append("No significant findings or directives in this cycle.")

        summary_text = "\n".join(summary_lines)

        reflection_ctx = MemoryHookContext(
            task_id=state.task_id,
            user_id=getattr(state, "user_id", None),
            phase="reflection",
        )

        self.c3_hooks.on_reflection_summary(
            summary=summary_text,
            context=reflection_ctx,
            extra_metadata={
                "final_output_preview": str(final_output)[:256],
                "has_error": bool(error),
            },
        )

        # 9.3 Optionally store a compact trace snippet
        snippet = f"final_output={str(final_output)[:256]}, error={error}"
        self.c3_hooks.on_trace_snippet(
            snippet=snippet,
            context=reflection_ctx,
            extra_metadata={
                "route_mode": str(route_mode),
            },
        )

        TraceLogger.log_final(state, final_output)

        # 10. Meta-cognition (C6)
        # ---------------------------------------------------------
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
        # ---------------------------------------------------------
        if getattr(state, "debug_visualize_plan", False):
            from brain.c2.plan_visualizer import PlanVisualizer
            state.plan_visualization = PlanVisualizer.visualize(plan)

        return final_output
