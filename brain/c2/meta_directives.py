from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional


class PlanningMode(Enum):
    SINGLE_STEP = "single_step"
    MULTI_STEP = "multi_step"
    TOOL_AWARE = "tool_aware"
    MEMORY_AWARE = "memory_aware"
    HYBRID = "hybrid"


@dataclass
class C2Directive:
    mode: PlanningMode
    notes: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None
