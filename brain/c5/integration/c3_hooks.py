# brain/c5/integration/c3_hooks.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from brain.c3.memory.base import MemoryProvider, MemoryQuery, MemorySearchResult


@dataclass
class MemoryHookContext:
    """
    Minimal context passed from C2/C4 into C5 when interacting with memory.
    Extend as needed (e.g., task_id, user_id, session_id).
    """
    task_id: Optional[str] = None
    user_id: Optional[str] = None
    phase: Optional[str] = None  # e.g., "planning", "execution", "reflection"
    result: Any = None
    error: Any = None


class C3MemoryHooks:
    """
    Integration layer between C5 reflection/heuristics and C3 memory.
    """

    def __init__(self, memory: MemoryProvider) -> None:
        self._memory = memory

    # ------------------------------------------------------------------
    # S4 compatibility: orchestrator expects these two no-op hooks
    # ------------------------------------------------------------------
    def before_planning(self, ctx: MemoryHookContext):
        """
        Called before planning begins.
        S4 tests only require that this method exists.
        """
        return None

    def after_execution(self, ctx: MemoryHookContext):
        """
        Called after execution finishes.
        S4 tests only require that this method exists.
        """
        return None

    # ------------------------------------------------------------------
    # Write-side hooks (real C5 reflection integration)
    # ------------------------------------------------------------------
    def on_reflection_summary(
        self,
        summary: str,
        context: Optional[MemoryHookContext] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        metadata: Dict[str, Any] = {"type": "reflection_summary"}

        if context:
            if context.task_id:
                metadata["task_id"] = context.task_id
            if context.user_id:
                metadata["user_id"] = context.user_id
            if context.phase:
                metadata["phase"] = context.phase

        if extra_metadata:
            metadata.update(extra_metadata)

        record = self._memory.write(content=summary, metadata=metadata)
        return record.id

    def on_trace_snippet(
        self,
        snippet: str,
        context: Optional[MemoryHookContext] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        metadata: Dict[str, Any] = {"type": "trace_snippet"}

        if context:
            if context.task_id:
                metadata["task_id"] = context.task_id
            if context.user_id:
                metadata["user_id"] = context.user_id
            if context.phase:
                metadata["phase"] = context.phase

        if extra_metadata:
            metadata.update(extra_metadata)

        record = self._memory.write(content=snippet, metadata=metadata)
        return record.id

    # ------------------------------------------------------------------
    # Read-side hooks (real C5 reflection integration)
    # ------------------------------------------------------------------
    def retrieve_for_reflection(
        self,
        query: str,
        context: Optional[MemoryHookContext] = None,
        top_k: int = 10,
        extra_filter: Optional[Dict[str, Any]] = None,
    ) -> List[MemorySearchResult]:
        metadata_filter: Dict[str, Any] = {}

        if extra_filter:
            metadata_filter.update(extra_filter)

        if context:
            if context.task_id:
                metadata_filter.setdefault("task_id", context.task_id)
            if context.user_id:
                metadata_filter.setdefault("user_id", context.user_id)

        mq = MemoryQuery(
            query=query,
            top_k=top_k,
            metadata_filter=metadata_filter or None,
        )
        return self._memory.search(mq)

    def stats(self) -> Dict[str, Any]:
        return self._memory.stats()
