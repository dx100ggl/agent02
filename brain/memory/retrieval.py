from brain.memory.store import LocalMemoryStore

# Placeholder for future vector search
class MemoryRetrieval:
    def __init__(self, store: LocalMemoryStore):
        self.store = store

    def search(self, query: str, k: int = 5):
        return self.store.query(query, k)
