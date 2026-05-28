from __future__ import annotations

from typing import Any, Dict, Optional

from brain.c3.memory.base import MemoryProvider
from brain.c4.tools.base import Tool  # adjust import if needed


class WriteMemoryTool(Tool):
    """
    Tool: write_memory
    Allows the agent to store new information into C3 memory.
    """

    def __init__(self, memory: MemoryProvider) -> None:
        self._memory = memory

    @property
    def name(self) -> str:
        return "write_memory"

    @property
    def description(self) -> str:
        return (
            "Write a new memory to the long-term memory store. "
            "Use this for durable facts, decisions, or summaries."
        )

    @property
    def args_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The text content to store in memory.",
                },
                "metadata": {
                    "type": "object",
                    "description": "Optional metadata (e.g., source, tags, task_id).",
                },
            },
            "required": ["content"],
        }

    def run(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        **_: Any,
    ) -> Dict[str, Any]:
        record = self._memory.write(content=content, metadata=metadata)

        return {
            "id": record.id,
            "content": record.content,
            "metadata": record.metadata,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }
