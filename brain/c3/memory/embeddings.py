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


# Example placeholder for a real embedding model using your LLM stack.
# Wire this to brain.llm.lmstudio_llm when you’re ready.
class LMStudioEmbeddingModel(EmbeddingModel):
    def __init__(self, client: object) -> None:
        self._client = client

    def embed_text(self, text: str) -> List[float]:
        # Implement when LM Studio embedding endpoint is available.
        # For now, you can just delegate to DummyEmbeddingModel or raise.
        raise NotImplementedError("LMStudioEmbeddingModel.embed_text is not implemented yet.")
