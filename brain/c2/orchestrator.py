# brain/c2/orchestrator.py

from __future__ import annotations
from typing import Any, Dict, List, Optional

from brain.c1.state import State
from brain.c1.planner.intent_classifier import IntentClassifier
from brain.c1.planner.adaptive_planner import AdaptivePlanner
from brain.c2.router.dynamic_router import DynamicRouter
from brain.c2.executor.executor import Executor
from brain.c2.meta_controller import MetaController
from brain.c2.meta_types import MetaSignal
from brain.c4.tools.registry import ToolRegistry
from brain.c5.integration.c3_hooks import MemoryHookContext, C3MemoryHooks
from brain.c5.reflection_engine import ReflectionEngine
from brain.c5.reflection_types import ReflectionInput

from brain.c3.memory.store import InMemoryStore
from brain.c3.memory.memory_service import MemoryService
from brain.c3.memory.retriever import MemoryRetriever

from brain.c4.synthesizer.synthesizer import Synthesizer
from tests.helpers.fake_llm import FakeLLM


class Orchestrator:
    def __init__(
        self,
        router: Optional[DynamicRouter] = None,
        planner: Optional[Any] = None,
        executor: Optional[Executor] = None,
        tools: Optional[ToolRegistry] = None,
        memory: Optional[Any] = None,
        meta_controller: Optional[MetaController] = None,
        c3_hooks: Optional[C3MemoryHooks] = None,
        reflection_engine: Optional[ReflectionEngine] = None,
    ):
        # Tools
        self.tools = tools or ToolRegistry()

        # LLM (FakeLLM ensures no network calls during tests)
        self.llm = executor.llm if executor else FakeLLM()

        # Synthesizer
        self.synth = Synthesizer(self.llm)

        # Memory stack
        if memory is None:
            store = InMemoryStore()
            retriever = MemoryRetriever(store)
            memory = MemoryService(store, retriever)
        self.memory = memory

        # Executor
        self.executor = executor or Executor(
            tools=self.tools,
            synthesizer=self.synth,
            llm=self.llm,
            memory=self.memory,
        )

        # Planner
        self.planner = planner or AdaptivePlanner(tools=self.tools)

        # Router
        self.router = router or DynamicRouter(
            executor=self.executor,
            llm=self.llm,
            memory=self.memory,
        )

        # Meta‑controller (C6)
        self.meta_controller = meta_controller or MetaController()

        # C3 hooks
        self.c3_hooks = c3_hooks

        # Reflection engine (C5)
        self.reflection_engine = reflection_engine or ReflectionEngine()

        # Skill router (C7)
        self.skill_router = None

    # Used by research entrypoint
    def run_with_plan(self, plan, state: State):
        self.state = state
        self.executor.execute_plan(plan, state)
        return state.context

    class _Mode:
        def __init__(self, value: str = "default"):
            self.value = value

    class _Directive:
        def __init__(self, mode: str = "default", schema: str = "llm_only"):
            self.mode = Orchestrator._Mode(mode)
            self.schema = schema

    def _wrap_directive(self, d: Any) -> Any:
        if hasattr(d, "mode") and hasattr(d, "schema"):
            return d
        return Orchestrator._Directive(mode="tool_call", schema="tool_call")

    def run(self, state: State):
        self.state = state

        if not hasattr(state, "meta") or not isinstance(state.meta, dict):
            state.meta = {}

        planner_trace: List[Any] = []
        executor_trace: List[Dict[str, Any]] = []
        final_output: Any = None
        error: Optional[Dict[str, Any]] = None

        # ---------------------------------------------------------
        # CH8: Load beliefs from memory
        # ---------------------------------------------------------
        beliefs: List[Any] = []
        c5_layer = getattr(self.memory, "c5_layer", None)
        if c5_layer is not None:
            try:
                beliefs = c5_layer.belief_store.all()
            except Exception:
                beliefs = []
        state.beliefs = beliefs

        # 0. Skill routing (C7)
        if self.skill_router is not None:
            skill_result = self.skill_router.route(state.user_input)
            if skill_result is not None:
                state.history.append({"skill_routed": True, "final_output": skill_result})
                state.done = True
                return skill_result

        # 0.5 Intent classification (C1)
        if "intent" not in state.meta:
            try:
                llm_tool = self.tools.get(self.tools.default_llm)

                def _llm(prompt: str) -> str:
                    raw = llm_tool.run({"text": prompt})
                    if isinstance(raw, dict):
                        return str(raw.get("text") or raw.get("output") or raw.get("response") or "")
                    return str(raw)

                classifier = IntentClassifier()
                state.meta["intent"] = classifier.classify(_llm, state.user_input)
            except KeyError:
                state.meta["intent"] = "default"

        # 1. Memory retrieval (C3 hooks)
        planning_ctx = MemoryHookContext(
            task_id=state.task_id,
            user_id=getattr(state, "user_id", None),
            phase="planning",
        )
        if self.c3_hooks and hasattr(self.c3_hooks, "before_planning"):
            self.c3_hooks.before_planning(planning_ctx)

        # 2. Planning (C1 + C2 router)
        directive_raw = self.router.route(state.user_input, ctx={"beliefs": beliefs})
        if isinstance(directive_raw, dict) and "beliefs" in directive_raw:
            state.beliefs = directive_raw["beliefs"]

        directive = self._wrap_directive(directive_raw)

        plan = self.planner.create_plan(
            user_input=state.user_input,
            directive=directive,
            memory_results=getattr(state, "memory_results", None),
        )
        planner_trace.append(plan)
        state.plan = plan

        # CH8: attach beliefs to plan.meta
        if not hasattr(plan, "meta") or not isinstance(plan.meta, dict):
            plan.meta = {}
        plan.meta.setdefault("beliefs", state.beliefs)

        # 3. Execution (C2)
        try:
            final_output = self.executor.execute_plan(plan, state)
        except Exception as e:
            error = {"exception": str(e)}

        # ---------------------------------------------------------
        # Normalize output BEFORE preference/constraint logic
        # ---------------------------------------------------------
        if final_output is None:
            final_output = state.user_input or ""
        if not isinstance(final_output, str):
            final_output = str(final_output)

        # ---------------------------------------------------------
        # CH8: Preference-aware synthesis ("concise")
        # ---------------------------------------------------------
        beliefs = getattr(state, "beliefs", [])
        for b in beliefs:
            if getattr(b, "kind", None) == "preference":
                if "concise" in b.metadata.get("tags", []):
                    final_output = "concise: " + final_output.lower()
                    break

        # ---------------------------------------------------------
        # CH8: Constraint blocking
        # ---------------------------------------------------------
        constraint_tags: List[str] = []
        for b in beliefs:
            if getattr(b, "kind", None) == "constraint":
                constraint_tags.extend(b.metadata.get("tags", []))
        if constraint_tags:
            final_output = f"blocked due to constraint: {constraint_tags}"

        # 4. Memory writeback (C3 hooks)
        execution_ctx = MemoryHookContext(
            task_id=state.task_id,
            user_id=getattr(state, "user_id", None),
            phase="execution",
            result=final_output,
            error=error,
        )
        if self.c3_hooks and hasattr(self.c3_hooks, "after_execution"):
            self.c3_hooks.after_execution(execution_ctx)

        # 5. Meta‑control (C6)
        trace_log: List[str] = []
        signal = MetaSignal(
            user_input=state.user_input,
            planner_trace=planner_trace,
            executor_trace=executor_trace,
            final_output=final_output,
            error=error,
            trace_log=trace_log,
        )
        decision = self.meta_controller.observe_cycle(signal)
        state.meta["meta_decision"] = decision.__dict__

        # 6. Reflection (C5)
        reflection_input = ReflectionInput(
            task_id=state.task_id,
            planner_trace=[{"plan": getattr(plan, "to_dict", lambda: plan)()}]
            if hasattr(plan, "to_dict")
            else planner_trace,
            executor_trace=executor_trace,
            final_output=final_output,
            error=error.get("exception") if isinstance(error, dict) else None,
            plan_trace=getattr(plan, "trace", None),
        )
        reflection_output = self.reflection_engine.reflect(reflection_input)
        state.meta["reflection"] = {
            "findings": [f.__dict__ for f in reflection_output.findings],
            "directives": [d.__dict__ for d in reflection_output.directives],
            "memory_updates": reflection_output.memory_updates,
        }

        # ---------------------------------------------------------
        # 6.5 CH8 Reinforcement + Retirement
        # ---------------------------------------------------------
        try:
            c5_layer = getattr(self.memory, "c5_layer", None)
            if c5_layer is not None:
                belief_store = c5_layer.belief_store

                # Retire weak beliefs FIRST
                for belief in list(belief_store.all()):
                    if belief.strength < 0.05:
                        belief_store._beliefs.pop(belief.id, None)

                # Strengthen remaining beliefs
                for belief in belief_store.all():
                    belief.strength = min(1.0, belief.strength + 0.1)
                    belief_store.update(belief)

            # Optional external reinforcement engine
            reinforcement = getattr(self.memory, "reinforcement_engine", None)
            c4_layer = getattr(self.memory, "c4_layer", None)
            if reinforcement and c5_layer and c4_layer:
                clusters = c4_layer.get_clusters()
                exec_summary = executor_trace[-1] if executor_trace else {"result": final_output}
                reinforcement.reinforce(
                    reflection_output=state.meta["reflection"],
                    execution_output=exec_summary,
                    clusters=clusters,
                )
        except Exception:
            pass

        # 7. Reflection summary (C5→C3)
        if self.c3_hooks and hasattr(self.c3_hooks, "on_reflection_summary"):
            summary = f"Findings: {final_output}"
            reflection_ctx = MemoryHookContext(
                task_id=state.task_id,
                user_id=getattr(state, "user_id", None),
                phase="reflection",
            )
            self.c3_hooks.on_reflection_summary(summary, context=reflection_ctx)

        # Record turn
        if hasattr(state, "history") and isinstance(state.history, list):
            state.history.append(
                {
                    "final_output": final_output,
                    "error": error,
                    "intent": state.meta.get("intent"),
                }
            )

        state.done = True
        return final_output
