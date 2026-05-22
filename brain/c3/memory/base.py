class MemoryStore:
    def put(self, item: dict):
        raise NotImplementedError

    def query(self, query: str, k: int = 5):
        raise NotImplementedError
