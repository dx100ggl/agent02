# brain/c3/memory/store.py

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class MemoryItem:
    """
    Unified MemoryItem supporting:
    - Legacy C1/C3 API: MemoryItem(text="...", tags=[...])
    - C3/C7 API: MemoryItem(key, value)
    """
    key: str
    value: Any
    tags: list[str] = None

    def __init__(self, key=None, value=None, text=None, tags=None):
        if text is not None:
            self.key = text
            self.value = text
            self.tags = tags or []
            return

        self.key = key
        self.value = value
        self.tags = tags or []

    @property
    def text(self) -> str:
        return str(self.value)


class MemoryStore:
    """
    Simple in-memory key-value store.
    Compatible with C1, C3, C4, C5, C7.
    """

    def __init__(self):
        self._store: Dict[str, Any] = {}

    def put(self, key: str, value: Any):
        self._store[key] = value

    def get(self, key: str):
        return self._store.get(key)

    # NEW: read wrapper for SkillStore
    def read(self, key: str):
        return self.get(key)

    def scan(self, prefix: str) -> Dict[str, Any]:
        return {k: v for k, v in self._store.items() if k.startswith(prefix)}

    def search(self, query: str) -> List[MemoryItem]:
        q = query.lower()
        results = []
        for k, v in self._store.items():
            if q in k.lower() or q in str(v).lower():
                results.append(MemoryItem(key=k, value=v))
        return results

    def add(self, text: str, tags=None):
        item = MemoryItem(text=text, tags=tags)
        self.put(item.key, item.value)

    def write(self, key: str, value: Any):
        self.put(key, value)
