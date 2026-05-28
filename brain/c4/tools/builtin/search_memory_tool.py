from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from brain.c3.memory.base import MemoryProvider, MemoryQuery, MemorySearchResult
from brain.c4.tools.base import Tool  # adjust import if needed


@dataclass
class SearchMemoryToolConfig:
    default_top_k: int = 5
    max_top_k: int = 20


class SearchMemoryTool(Tool):
    """
    Tool: search_memory
    Allows the agent to retrieve relevant past memories from C3.
    """

    def __init__(
        self,
        memory: MemoryProvider,
        config: Optional[SearchMemoryToolConfig] = None,
    ) -> None:
        self._memory = memory
        self._config = config or SearchMemoryToolConfig()

    @property
    def name(self) -> str:
        return "search_memory"

    @property
    def description(self) -> str:
        return (
            "Search the long-term memory store for relevant information. "
            "Useful for recalling prior conversations, tasks, or facts."
        )

    @property
    def args_schema(self) -> Dict[str, Any]:
        # If you use pydantic, replace with a proper model.
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language search query."},
                "top_k": {
                    "type": "integer",
                    "description": "Maximum number of results to return.",
                    "minimum": 1,
                    "maximum": self._config.max_top_k,
                },
                "metadata_filter": {
                    "type": "object",
                    "description": "Optional exact-match metadata filter.",
                },
            },
            "required": ["query"],
        }

    def run(
        self,
        query: str,
        top_k: Optional[int] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        **_: Any,
    ) -> List[Dict[str, Any]]:
        k = top_k or self._config.default_top_k
        k = max(1, min(k, self._config.max_top_k))

        mq = MemoryQuery(query=query, top_k=k, metadata_filter=metadata_filter)
        results: List[MemorySearchResult] = self._memory.search(mq)

        # Return a JSON-serializable structure
        return [
            {
                "id": r.record.id,
                "content": r.record.content,
                "metadata": r.record.metadata,
                "score": r.score,
                "created_at": r.record.created_at.isoformat(),
                "updated_at": r.record.updated_at.isoformat(),
            }
            for r in results
        ]
