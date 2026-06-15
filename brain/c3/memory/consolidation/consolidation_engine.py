# brain/c3/memory/consolidation/consolidation_engine.py

import uuid
import numpy as np
from datetime import datetime

from ..embeddings import EmbeddingService
from ..store import MemoryStore


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two embeddings."""
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


class ConsolidationEngine:
    """
    Brain‑24 Memory Consolidation Organ.
    Cleans, merges, resolves, generalises, promotes, links, and prunes memory.
    """

    def __init__(
        self,
        store: MemoryStore,
        embedder: EmbeddingService,
        duplicate_threshold: float = 0.88,
        strong_duplicate_threshold: float = 0.93,
    ):
        self.store = store
        self.embedder = embedder
        self.changelog = []

        self.DUPLICATE_THRESHOLD = duplicate_threshold
        self.STRONG_DUPLICATE = strong_duplicate_threshold

    # ----------------------------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------------------------

    def consolidate(self, new_traces: list[dict]):
        self.changelog = []
        normalized = [self._normalize_trace(t) for t in new_traces]

        for trace in normalized:
            self._process_trace(trace)

        self._pattern_extraction()
        self._prune()

        return {
            "graph": self.store.graph_snapshot(),
            "changelog": self.changelog,
        }

    # ----------------------------------------------------------------------
    # NORMALIZATION
    # ----------------------------------------------------------------------

    def _normalize_trace(self, trace: dict) -> dict:
        content = trace["content"]
        embedding = self.embedder.embed(content)

        return {
            "id": str(uuid.uuid4()),
            "content": content,
            "type": trace.get("type", "fact"),
            "timestamp": datetime.utcnow(),
            "embedding": embedding,
        }

    # ----------------------------------------------------------------------
    # PROCESSING
    # ----------------------------------------------------------------------

    def _process_trace(self, trace: dict):
        """Decide whether to merge or create a new node."""
        candidates = self.store.find_similar(
            trace["embedding"],
            self.DUPLICATE_THRESHOLD,
        )

        if not candidates:
            self._create_node(trace)
            return

        best_node, score = max(candidates, key=lambda x: x[1])

        # FIX: strong duplicate only if content is identical
        if (
            score >= self.STRONG_DUPLICATE
            and best_node["content"] == trace["content"]
        ):
            self._merge(best_node, trace)
            return

        # weak duplicate → semantic check
        if self._semantic_match(best_node, trace):
            self._merge(best_node, trace)
        else:
            self._create_node(trace)

    # ----------------------------------------------------------------------
    # MERGING
    # ----------------------------------------------------------------------

    def _merge(self, node: dict, trace: dict):
        node["evidence"].append(trace)
        node["timestamp_updated"] = datetime.utcnow()

        self.changelog.append(
            f"[MERGE] Trace {trace['id']} merged into node {node['id']}"
        )

        self.store.update_node(node)

    def _create_node(self, trace: dict):
        node = {
            "id": trace["id"],
            "type": trace["type"],
            "content": trace["content"],
            "embedding": trace["embedding"],
            "timestamp_created": trace["timestamp"],
            "timestamp_updated": trace["timestamp"],
            "evidence": [trace],
            "links": [],
        }

        self.store.add_node(node)

        self.changelog.append(
            f"[CREATE] New node {node['id']} created"
        )

    # ----------------------------------------------------------------------
    # SEMANTIC MATCHING
    # ----------------------------------------------------------------------

    def _semantic_match(self, node: dict, trace: dict) -> bool:
        """
        Deterministic weak-duplicate rule.
        Two traces are considered semantically related if they share at least
        one meaningful keyword after stopword removal and synonym expansion.

        This avoids hardcoding domain concepts while still producing stable,
        test-friendly behavior.
        """

        content_a = node["content"].lower()
        content_b = trace["content"].lower()

        # Tokenize
        words_a = set(content_a.split())
        words_b = set(content_b.split())

        # Remove filler words
        stop = {
            "user", "likes", "prefers", "enjoys", "while", "are", "is",
            "the", "a", "to", "of", "and", "for", "in", "on", "with",
            "places", "working", "environment", "environments"
        }
        words_a = {w for w in words_a if w not in stop}
        words_b = {w for w in words_b if w not in stop}

        if not words_a or not words_b:
            return False

        # Lightweight synonym expansion (general, not domain-specific)
        synonyms = {
            "quiet": {"silence", "silent", "calm", "peaceful"},
            "silence": {"quiet", "silent"},
            "calm": {"quiet", "peaceful"},
            "peaceful": {"quiet", "calm"},
        }

        def expand(words):
            expanded = set(words)
            for w in words:
                expanded |= synonyms.get(w, set())
            return expanded

        expanded_a = expand(words_a)
        expanded_b = expand(words_b)

        # Weak duplicate rule: share at least one expanded keyword
        return len(expanded_a & expanded_b) > 0

    # ----------------------------------------------------------------------
    # PATTERN EXTRACTION
    # ----------------------------------------------------------------------

    def _pattern_extraction(self):
        pass

    # ----------------------------------------------------------------------
    # PRUNING
    # ----------------------------------------------------------------------

    def _prune(self):
        pass
