# brain/research_entrypoint.py

from brain.c1.state import State
from brain.c1.planner.adaptive_planner import AdaptivePlanner

from brain.c2.orchestrator import Orchestrator
from brain.c2.executor.executor import Executor

from brain.c4.tools.registry import ToolRegistry
from brain.c4.synthesizer.synthesizer import Synthesizer

from brain.c3.memory.retriever import SimpleMemoryProvider
from brain.c3.memory.base import MemoryQuery

from brain.c5.reflection_engine import ReflectionEngine
from brain.c5.trace_logger import TraceLogger


class ResearchEngine:
    def __init__(self):
        self._tool_registry = ToolRegistry()
        self._memory = SimpleMemoryProvider()
        self._planner = AdaptivePlanner(tools=self._tool_registry)

        self._executor = Executor(
            tools=self._tool_registry,
            memory=self._memory,
        )
        self._orchestrator = Orchestrator(
            executor=self._executor,
            tools=self._tool_registry,
            memory=self._memory,
            planner=self._planner,
        )

        # ⭐ If you want real synthesis, plug in your LLM here:
        from brain.llm.lmstudio_llm import LMStudioLLM
        self._synthesizer = Synthesizer(llm=LMStudioLLM())
        # self._synthesizer = Synthesizer()

        self._trace_logger = TraceLogger()
        self._reflection_engine = ReflectionEngine()

    def run_research(self, query: str):
        # ---- C1: state ----
        state = State(user_input=query, memory=None, context={})

        # ---- C3: retrieve memory ----
        memory_hits = self._memory.search(
            MemoryQuery(query=query, top_k=5)
        )
        state.memory_results = memory_hits

        # ---- Force tool-based planning for research queries ----
        state.meta["directive"] = {
            "mode": "tool_call",
            "schema": "tool_call",
        }

        # ---- C2: orchestrator handles planning + execution ----
        final_output = self._orchestrator.run(state)

        # ---- Build research sections for Synthesizer ----
        ctx = state.context or {}

        # ⭐ Correct ticker extraction
        state.meta["ticker"] = (
            ctx.get("market_data", {}).get("ticker", "UNKNOWN")
        )

        # ⭐ Correct section mapping
        state.meta["research_sections"] = {
            "technical": ctx.get("market_data", {}),
            "options": ctx.get("options_data", {}),
            "sentiment": ctx.get("sentiment", {}),
            "macro": ctx.get("macro", {}),
            "analogs": ctx.get("analogs", {}),
        }

        # ---- Ensure Synthesizer fallback works ----
        if state.history:
            last = state.history[-1]
            if "result" not in last:
                last["result"] = last.get("final_output", "")

        # ---- C4: synthesis ----
        synthesis = self._synthesizer.synthesize(state)

        # ---- C3: write memory ----
        self._memory.write(
            content=synthesis,
            metadata={"query": query},
        )

        # ---- C5: reflection ----
        from brain.c5.reflection_types import ReflectionInput

        reflection_input = ReflectionInput(
            task_id=state.task_id,
            planner_trace=[],
            executor_trace=[],
            final_output=synthesis,
            error=None,
            plan_trace=None,
        )

        reflections = self._reflection_engine.reflect(reflection_input)

        # ---- C5: trace logging ----
        self._trace_logger.log_final(state, synthesis)
        self._trace_logger.log_reflection(state, reflections)

        return {
            "query": query,
            "plan": state.plan,
            "tool_traces": [],
            "tool_outputs": state.context,
            "synthesis": synthesis,
            "reflections": reflections,
        }


_engine = None

def run_research(query: str):
    global _engine
    if _engine is None:
        _engine = ResearchEngine()
    return _engine.run_research(query)
