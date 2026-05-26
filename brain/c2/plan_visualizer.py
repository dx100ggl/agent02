from typing import List, Dict, Any
from brain.c1.planner.plan import Plan


class PlanVisualizer:
    """
    Pretty-printer for Plan + Trace.
    Produces a clean, readable text representation.
    """

    @staticmethod
    def visualize(plan: Plan) -> str:
        lines = []

        lines.append("=== PLAN ===")
        lines.append(f"User Input: {plan.user_input}")
        lines.append("")

        lines.append("Steps:")
        if not plan.steps:
            lines.append("  (none)")
        else:
            for i, step in enumerate(plan.steps):
                lines.append(f"  [{i}] {step.description}")
                if step.tool:
                    lines.append(f"       tool: {step.tool}")
                if step.args:
                    lines.append(f"       args: {step.args}")
                if step.result is not None:
                    lines.append(f"       result: {step.result}")

        lines.append("")
        lines.append("=== TRACE ===")

        if not plan.trace:
            lines.append("  (no trace events)")
        else:
            for event in plan.trace:
                e = event.get("event")
                d = event.get("data", {})
                lines.append(f"- {e}: {d}")

        lines.append("")
        lines.append("=== META ===")
        if plan.meta:
            for k, v in plan.meta.items():
                lines.append(f"{k}: {v}")
        else:
            lines.append("(no meta)")

        return "\n".join(lines)
