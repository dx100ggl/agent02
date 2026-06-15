# brain/c3/memory/consolidation/consolidation_engine.py

import uuid
import numpy as np
from datetime import datetime, timezone

from ..embeddings import EmbeddingService
from ..store import MemoryStore


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


# ============================================================
# ORGAN 1 — Trace Normalizer
# ============================================================

class TraceNormalizer:
    """
    C3 Normalization organ.
    Turns raw traces into canonical, embedded traces.
    """

    def __init__(self, embedder: EmbeddingService):
        self.embedder = embedder

    def normalize(self, trace: dict) -> dict:
        content = trace["content"]
        embedding = self.embedder.embed(content)

        return {
            "id": str(uuid.uuid4()),
            "content": content,
            "type": trace.get("type", "fact"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "embedding": embedding,
        }


# ============================================================
# ORGAN 2 — Duplicate Resolver
# ============================================================

class DuplicateResolver:
    """
    C3 Duplicate resolution organ.
    Decides MERGE vs CREATE for each normalized trace.
    """

    def __init__(
        self,
        store: MemoryStore,
        duplicate_threshold: float,
        strong_duplicate_threshold: float,
        semantic_match_fn,
    ):
        self.store = store
        self.duplicate_threshold = duplicate_threshold
        self.strong_duplicate_threshold = strong_duplicate_threshold
        self.semantic_match_fn = semantic_match_fn

    def process(self, trace: dict, changelog: list):
        candidates = self.store.find_similar(
            trace["embedding"],
            self.duplicate_threshold,
        )

        if not candidates:
            self._create_node(trace, changelog)
            return

        best_node, score = max(candidates, key=lambda x: x[1])

        # Strong duplicate only if content identical
        if score >= self.strong_duplicate_threshold and best_node["content"] == trace["content"]:
            self._merge(best_node, trace, changelog)
            return

        # Weak duplicate → semantic check
        if self.semantic_match_fn(best_node, trace):
            self._merge(best_node, trace, changelog)
        else:
            self._create_node(trace, changelog)

    def _merge(self, node: dict, trace: dict, changelog: list):
        node["evidence"].append(trace)
        node["timestamp_updated"] = datetime.now(timezone.utc).isoformat()

        changelog.append(
            f"[MERGE] Trace {trace['id']} merged into node {node['id']}"
        )

        self.store.update_node(node)

    def _create_node(self, trace: dict, changelog: list):
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

        changelog.append(
            f"[CREATE] New node {node['id']} created"
        )


# ============================================================
# C3 CONSOLIDATION ENGINE (now orchestrating organs)
# ============================================================

class ConsolidationEngine:
    """
    Brain‑24 Memory Consolidation Organ.
    Now orchestrates modular organs.
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
        self.changelog: list[str] = []

        # Organs
        self.normalizer = TraceNormalizer(embedder)
        self.duplicate_resolver = DuplicateResolver(
            store=store,
            duplicate_threshold=duplicate_threshold,
            strong_duplicate_threshold=strong_duplicate_threshold,
            semantic_match_fn=self._semantic_match,
        )

    # ----------------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------------

    def consolidate(self, new_traces: list[dict]):
        self.changelog = []

        normalized = [self.normalizer.normalize(t) for t in new_traces]

        for trace in normalized:
            self.duplicate_resolver.process(trace, self.changelog)

        self._pattern_extraction()
        self._prune()

        return {
            "graph": self.store.graph_snapshot(),
            "changelog": self.changelog,
        }

    # ----------------------------------------------------------
    # SEMANTIC MATCHING (unchanged)
    # ----------------------------------------------------------

    def _semantic_match(self, node: dict, trace: dict) -> bool:
        content_a = node["content"].lower()
        content_b = trace["content"].lower()

        words_a = set(content_a.split())
        words_b = set(content_b.split())

        stop = {
            "user", "likes", "prefers", "enjoys", "while", "are", "is",
            "the", "a", "to", "of", "and", "for", "in", "on", "with",
            "places", "working", "environment", "environments"
        }
        words_a = {w for w in words_a if w not in stop}
        words_b = {w for w in words_b if w not in stop}

        if not words_a or not words_b:
            return False

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

        return len(expanded_a & expanded_b) > 0

    # ----------------------------------------------------------
    # FUTURE ORGANS
    # ----------------------------------------------------------

    def _pattern_extraction(self):
        pass

    def _prune(self):
        pass
