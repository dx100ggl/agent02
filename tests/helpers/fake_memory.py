# tests/helpers/fake_memory.py

from typing import List, Dict, Any
from brain.c3.memory.base import MemoryProvider, MemoryQuery, MemoryRecord


class FakeMemory(MemoryProvider):
    """
    Minimal fake memory provider for tests.
    """

    def __init__(self):
        self._records: List[MemoryRecord] = []

    def write(self, content: str, metadata: dict):
        self._records.append(
            MemoryRecord(content=content, metadata=metadata)
        )

    def search(self, query: MemoryQuery):
        # Return all records; no embedding logic needed for tests
        class Result:
            def __init__(self, record):
                self.record = record

        return [Result(r) for r in self._records]

    def delete(self, metadata_filter: Dict[str, Any] | None = None) -> int:
        """
        No‑op delete for tests.
        Returns number of deleted records (0 for now).
        """
        return 0

    def stats(self) -> Dict[str, Any]:
        """
        Minimal stats for tests.
        """
        return {
            "count": len(self._records),
        }
