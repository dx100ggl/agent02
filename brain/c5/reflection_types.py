from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ReflectionInput:
    """
    Input to the Reflection Engine.
    """
    task_id: str
    planner_trace: List[Dict[str, Any]]
    executor_trace: List[Dict[str, Any]]
    final_output: Any
    error: Optional[str] = None
    plan_trace: Optional[List[Dict[str, Any]]] = None


@dataclass
class ReflectionFinding:
    """
    A detected issue or insight from reflection.
    """
    category: str
    description: str
    evidence: str


@dataclass
class ReflectionDirective:
    """
    A short, actionable rule for improving future behavior.
    """
    directive: str
    priority: int


@dataclass
class ReflectionOutput:
    """
    The full result of a reflection cycle.
    """
    findings: List[ReflectionFinding]
    directives: List[ReflectionDirective]
    memory_updates: Dict[str, Any]
