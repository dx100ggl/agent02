from typing import List, Dict, Any, Optional

from brain.c3.memory.store import MemoryStore, MemoryItem
from brain.c1.state import BrainState


class MemoryRetriever:
    """
    High-level retrieval interface for Memory v2.
    """

    def __init__(self, store: Optional[MemoryStore] = None, min_score: float = 0.3):
        self.store = store or MemoryStore()
        self.min_score = min_score

    def retrieve(self, state: BrainState, top_k: int = 5) -> List[Dict[str, Any]]:
        query = state.user_input or ""
        if not query:
            return []

        items = self.store.search(query, top_k=top_k)

        # Recompute scores for transparency
        embedder = self.store.embedder
        q_vec = embedder.embed(query)

        from brain.c3.memory.store import MemoryStore as _MS

        results = []
        for item in items:
            sim = _MS._cosine(q_vec, item.vector)
            kw_bonus = 0.1 if query.lower() in item.text.lower() else 0.0
            score = sim + kw_bonus

            if score >= self.min_score:
                results.append({
                    "id": item.id,
                    "text": item.text,
                    "metadata": item.metadata,
                    "score": score,
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results
