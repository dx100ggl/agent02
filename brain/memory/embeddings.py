from typing import List
import math
import hashlib


class SimpleEmbedder:
    """
    Deterministic, dependency-free embedder for Memory v2.

    - Not meant to be "good", just stable and testable.
    - Uses a hash-based projection into a fixed-size vector.
    """

    def __init__(self, dim: int = 32):
        self.dim = dim

    def embed(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dim

        # Hash the text and spread bits across dimensions
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vals = [b for b in h]

        # Repeat / trim to match dim
        while len(vals) < self.dim:
            vals.extend(vals)
        vals = vals[:self.dim]

        # Normalize to [0, 1]
        vec = [v / 255.0 for v in vals]

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]
