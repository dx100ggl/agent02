# brain/research_entrypoint.py

from __future__ import annotations
from typing import Dict, Any

from brain.c4.tools.registry import ToolRegistry
from brain.c4.synthesizer.synthesizer import Synthesizer
from brain.llm.lmstudio_llm import LMStudioLLM

from brain.c2.executor.executor import Executor
from brain.c2.router.dynamic_router import DynamicRouter

from brain.c3.memory.store import MemoryStore
from brain.c3.memory.retriever import MemoryRetriever
from brain.c3.memory.memory_service import MemoryService


class ResearchEngine:
    """
    New C1 → C2 → C3 → C4 research engine.
    - C2 DynamicRouter chooses plan (fundamentals for now)
    - C3 MemoryService retrieves memory
    - C2 Executor runs plan steps
    - C4 Synthesizer produces final output
    """

    def __init__(self):
        # -----------------------------
        # C4: Tools
        # -----------------------------
        self._tool_registry = ToolRegistry()

        # -----------------------------
        # LLM
        # -----------------------------
        self._llm = LMStudioLLM()

        # -----------------------------
        # C4: Synthesizer
        # -----------------------------
        self._synthesizer = Synthesizer(llm=self._llm)

        # -----------------------------
        # C3: Memory
        # -----------------------------
        store = MemoryStore()
        retriever = MemoryRetriever(store)
        self._memory = MemoryService(store, retriever)

        # -----------------------------
        # C2: Executor
        # -----------------------------
        self._executor = Executor(
            tools=self._tool_registry,
            synthesizer=self._synthesizer,
            llm=self._llm,
        )

        # -----------------------------
        # C2: Router (memory‑aware)
        # -----------------------------
        self._router = DynamicRouter(
            executor=self._executor,
            llm=self._llm,
            memory=self._memory,
        )

    # ------------------------------------------------------------------
    # Public entrypoint
    # ------------------------------------------------------------------
    def run_research(self, query: str) -> Dict[str, Any]:
        """
        Full C1 → C2 → C3 → C4 pipeline.
        """
        exec_ctx = self._router.route(query, ctx={})

        # Final synthesized output is in exec_ctx["final"]["result"]
        final = exec_ctx.get("final", {})
        result = final.get("result", "")

        # Write memory (C3)
        self._memory.store.add(
            content=result,
            metadata={"query": query},
        )

        return {
            "query": query,
            "execution": exec_ctx,
            "result": result,
        }


_engine = None


def run_research(query: str):
    global _engine
    if _engine is None:
        _engine = ResearchEngine()
    return _engine.run_research(query)
