# brain/c4/normalizers/normalizer_base.py

from __future__ import annotations
from typing import Any, Dict


class Normalizer:
    """
    Base class for all C4 normalizers.
    Each tool returns raw data → normalizer extracts clean signals.
    """

    def normalize(self, raw: Any) -> Dict[str, Any]:
        raise NotImplementedError
