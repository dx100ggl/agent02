# brain/c3/memory/embeddings.py

from __future__ import annotations

from typing import List

from .base import EmbeddingModel


class DummyEmbeddingModel(EmbeddingModel):
    """
    Simple deterministic embedding for bootstrapping and tests.
    Replace with a real model (e.g., LM Studio) when ready.
    """

    def embed_text(self, text: str) -> List[float]:
        # Very cheap, order-invariant hash-based embedding
        h = abs(hash(text))
        return [
            (h % 97) / 97.0,
            (h % 193) / 193.0,
            (h % 389) / 389.0,
        ]


class LMStudioEmbeddingModel(EmbeddingModel):
    """
    Placeholder for a real embedding model using your LM Studio LLM stack.
    """

    def __init__(self, client: object) -> None:
        self._client = client

    def embed_text(self, text: str) -> List[float]:
        # Implement when LM Studio embedding endpoint is available.
        raise NotImplementedError("LMStudioEmbeddingModel.embed_text is not implemented yet.")


# ----------------------------------------------------------------------
# NEW: EmbeddingService (required by MemoryService + ConsolidationEngine)
# ----------------------------------------------------------------------

class EmbeddingService:
    """
    High-level embedding wrapper used by MemoryService and ConsolidationEngine.

    Default backend: DummyEmbeddingModel (deterministic, test-friendly).
    Swap in LMStudioEmbeddingModel or any other EmbeddingModel when ready.
    """

    def __init__(self, model: EmbeddingModel | None = None):
        # If no model is provided, use the deterministic dummy model.
        self.model = model or DummyEmbeddingModel()

    def embed(self, text: str) -> List[float]:
        """
        Public API used by all memory components.
        """
        return self.model.embed_text(text)
