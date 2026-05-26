from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MemoryItem:
    text: str
    tags: Optional[List[str]] = None
    importance: float = 1.0


class MemoryStore:
    """
    Simple memory store with:
    - append
    - keyword search
    - tag filtering
    """

    def __init__(self):
        self.items: List[MemoryItem] = []

    def add(self, text: str, tags=None, importance=1.0):
        self.items.append(MemoryItem(text=text, tags=tags, importance=importance))

    def search(self, query: str) -> List[MemoryItem]:
        q = query.lower()
        results = []

        for item in self.items:
            if q in item.text.lower():
                results.append(item)
                continue

            if item.tags and any(q in tag.lower() for tag in item.tags):
                results.append(item)

        results.sort(key=lambda x: x.importance, reverse=True)
        return results
