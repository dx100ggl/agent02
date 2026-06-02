# brain/c4/tools/builtin/options_cache.py

import time
from typing import Any, Dict, Tuple


class OptionsDataCache:
    def __init__(self, ttl_seconds: float = 45.0):
        self.ttl = ttl_seconds
        self._store: Dict[Tuple, Tuple[float, Any]] = {}

    def get(self, key: Tuple) -> Any | None:
        entry = self._store.get(key)
        if not entry:
            return None
        ts, value = entry
        if time.time() - ts > self.ttl:
            return None
        return value

    def set(self, key: Tuple, value: Any) -> None:
        self._store[key] = (time.time(), value)
