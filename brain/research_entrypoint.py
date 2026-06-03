# brain/research_entrypoint.py

from __future__ import annotations
from typing import Dict, Any

from brain.c4.tools.registry import ToolRegistry
from brain.c4.synthesizer.synthesizer import Synthesizer
from brain.llm.lmstudio_llm import LMStudioLLM

from brain.c2.executor.executor import Executor
from brain.c2.router.dynamic_router import DynamicRouter

from brain.c3.memory.store import InMemoryStore
from brain.c3.memory.retriever import MemoryRetriever
from brain.c3.memory.memory_service import MemoryService
from brain.c3.memory.base import MemoryRecord

from brain.c4.normalizers.section_normalizer import SectionNormalizer


class ResearchEngine:
    """
    New C1 → C2 → C3 → C4 research engine.
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
        store = InMemoryStore()
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

        # -----------------------------
        # C4: Normalizer
        # -----------------------------
        self._normalizer = SectionNormalizer()

    # ------------------------------------------------------------------
    # Public entrypoint
    # ------------------------------------------------------------------
    def run_research(self, query: str) -> Dict[str, Any]:
        """
        Full C1 → C2 → C3 → C4 pipeline.
        """
        exec_ctx = self._router.route(query, ctx={})

        # -----------------------------
        # Extract final step output
        # -----------------------------
        final_step = exec_ctx.get("final", {})
        raw_outputs = final_step.get("result", {})

        # -----------------------------
        # Normalize tool outputs (C4)
        # -----------------------------
        if isinstance(raw_outputs, dict):
            normalized_sections = self._normalizer.normalize(raw_outputs)
            ticker = raw_outputs.get("ticker", "UNKNOWN")
        else:
            normalized_sections = {}
            ticker = "UNKNOWN"

        # -----------------------------
        # Synthesize full research report (C4)
        # -----------------------------
        report = self._synthesizer.synthesize_from_sections(
            ticker=ticker,
            intent=query,
            sections=normalized_sections,
        )

        # -----------------------------
        # Write memory (C3)
        # -----------------------------
        record = MemoryRecord(
            id=f"research:{query}",
            content=report,
            embedding=None,
            metadata={"query": query},
        )
        self._memory.store.add(record)

        return {
            "query": query,
            "execution": exec_ctx,
            "normalized": normalized_sections,
            "result": report,
        }


_engine = None


def run_research(query: str):
    global _engine
    if _engine is None:
        _engine = ResearchEngine()
    return _engine.run_research(query)
