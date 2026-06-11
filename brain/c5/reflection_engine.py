# brain/c5/reflection_engine.py

from typing import Optional, List

from .reflection_types import (
    ReflectionInput,
    ReflectionOutput,
    ReflectionFinding,
    ReflectionDirective,
)


class ReflectionEngineV1:
    """
    Deterministic, rule-based reflection engine.
    Produces findings, directives, and memory updates.
    """

    def reflect(self, r: ReflectionInput) -> ReflectionOutput:
        findings: List[ReflectionFinding] = []
        directives: List[ReflectionDirective] = []
        memory_updates = {}

        if self._detect_missing_preconditions(r):
            findings.append(ReflectionFinding(
                category="planning_error",
                description="Planner executed steps without required preconditions.",
                evidence="Trace analysis",
            ))
            directives.append(ReflectionDirective(
                directive="Ensure precondition checks before tool calls.",
                priority=5,
            ))

        misuse = self._detect_tool_misuse(r)
        if misuse:
            findings.append(ReflectionFinding(
                category="tool_misuse",
                description=misuse,
                evidence="Executor trace",
            ))
            directives.append(ReflectionDirective(
                directive="Validate tool arguments against schema.",
                priority=4,
            ))

        halluc = self._detect_hallucination(r)
        if halluc:
            findings.append(ReflectionFinding(
                category="hallucination",
                description=halluc,
                evidence="Output vs trace mismatch",
            ))
            directives.append(ReflectionDirective(
                directive="Cross-check claims against memory or tools.",
                priority=5,
            ))

        if self._detect_redundancy(r):
            findings.append(ReflectionFinding(
                category="efficiency",
                description="Redundant or repeated steps detected.",
                evidence="Planner trace",
            ))
            directives.append(ReflectionDirective(
                directive="Avoid repeating identical tool calls.",
                priority=2,
            ))

        memory_updates = self._derive_memory_updates(findings, directives)

        # Plan-trace driven mode adjustment
        if r.plan_trace:
            for event in r.plan_trace:
                if event["event"] == "step_result":
                    result = event["data"].get("result", {})
                    if isinstance(result, dict) and result.get("error"):
                        directives.append(
                            ReflectionDirective(
                                directive="adjust_mode:more_cautious",
                                priority=5,
                            )
                        )

        return ReflectionOutput(
            findings=findings,
            directives=directives,
            memory_updates=memory_updates,
        )

    def _detect_missing_preconditions(self, r: ReflectionInput) -> bool:
        for event in r.planner_trace:
            if isinstance(event, dict):
                if event.get("type") == "precondition_check":
                    if not event.get("satisfied", True):
                        return True
        return False


    def _detect_tool_misuse(self, r: ReflectionInput) -> Optional[str]:
        for event in r.executor_trace:
            if not isinstance(event, dict):
                continue
            if event.get("error"):
                tool = event.get("tool", "unknown_tool")
                return f"Tool '{tool}' failed with error: {event['error']}"
        return None


    def _detect_hallucination(self, r: ReflectionInput) -> Optional[str]:
        output = str(r.final_output).lower()

        # Collect executed tool names
        executed_tools = {
            str(e.get("tool")).lower()
            for e in r.executor_trace
            if isinstance(e, dict) and e.get("tool")
        }

        # If output mentions a tool that was never executed
        for word in output.split():
            if word.endswith("_tool") and word.lower() not in executed_tools:
                return f"Output referenced '{word}' but no such tool was executed."

        return None


    def _detect_redundancy(self, r: ReflectionInput) -> bool:
        seen = set()
        for event in r.executor_trace:
            if not isinstance(event, dict):
                continue
            sig = (
                event.get("tool"),
                tuple(sorted((event.get("args") or {}).items()))
            )
            if sig in seen:
                return True
            seen.add(sig)
        return False


    def _derive_memory_updates(self, findings, directives):
        updates = {}

        for f in findings:
            if f.category == "hallucination":
                updates["caution_level"] = "high"
            if f.category == "tool_misuse":
                updates.setdefault("tool_misuse_count", 0)
                updates["tool_misuse_count"] += 1
            if f.category == "efficiency":
                updates["optimize_redundancy"] = True

        return updates



ReflectionEngine = ReflectionEngineV1
