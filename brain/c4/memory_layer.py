# brain/c4/memory_layer.py

from .clustering.cluster_store import InMemoryClusterStore
from .clustering.clusterer import SimpleKeywordClusterer
from brain.c3.memory.store import InMemoryStore


class C4SemanticLayer:
    def __init__(self, c3_store: InMemoryStore):
        self.cluster_store = InMemoryClusterStore()
        self.clusterer = SimpleKeywordClusterer(c3_store, self.cluster_store)

    def rebuild_clusters(self):
        self.clusterer.run()

    def get_clusters(self):
        return self.cluster_store.all()
