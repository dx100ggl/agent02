from brain.memory.base import MemoryStore

class LocalMemoryStore(MemoryStore):
    def __init__(self):
        self.data = []

    def put(self, item):
        self.data.append(item)

    def query(self, query, k=5):
        return [x for x in self.data if query.lower() in x["text"].lower()][:k]
