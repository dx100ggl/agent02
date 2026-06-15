# brain/c5/memory_layer.py

from brain.c4.memory_layer import C4SemanticLayer
from brain.c5.beliefs.belief_store import InMemoryBeliefStore
from brain.c5.beliefs.belief_promoter import SimpleBeliefPromoter


class C5BeliefLayer:
    """
    C5 layer: stable beliefs over C4 clusters.
    """

    def __init__(self, c4_layer: C4SemanticLayer):
        self.c4_layer = c4_layer
        self.belief_store = InMemoryBeliefStore()
        self.promoter = SimpleBeliefPromoter(self.belief_store, min_size=2)

    def rebuild_beliefs(self):
        self.c4_layer.rebuild_clusters()
        clusters = self.c4_layer.get_clusters()
        self.promoter.promote_from_clusters(clusters)

    def get_beliefs(self):
        return self.belief_store.all()
