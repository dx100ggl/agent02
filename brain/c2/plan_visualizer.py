# brain/c2/plan_visulizer.py

from typing import List, Dict, Any
from brain.c1.planner.plan import Plan
from brain.c2.process_model import (
    ProcessModel,
    ProcessNode,
    ProcessEdge,
    NodeKind,
    EdgeKind,
)


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

class ProcessGraphVisualizer:
    """
    Renders a ProcessModel as a simple ASCII or GraphViz-style diagram.
    This is intentionally lightweight and dependency-free.
    """

    def __init__(self, model: ProcessModel):
        self.model = model

    # ---------------------------------------------------------
    # ASCII rendering
    # ---------------------------------------------------------
    def to_ascii(self) -> str:
        lines = []
        lines.append(f"ProcessModel(id={self.model.id})")
        lines.append("")

        # Nodes
        lines.append("Nodes:")
        for node_id, node in self.model.nodes.items():
            lines.append(f"  - {node_id} [{node.kind.name}]")
        lines.append("")

        # Edges
        lines.append("Edges:")
        for e in self.model.edges:
            cond = "cond" if e.condition else ""
            lines.append(f"  {e.source} -> {e.target} ({e.kind.name}) {cond}")
        lines.append("")

        return "\n".join(lines)

    # ---------------------------------------------------------
    # GraphViz DOT rendering
    # ---------------------------------------------------------
    def to_dot(self) -> str:
        out = []
        out.append("digraph ProcessModel {")
        out.append('  rankdir="LR";')

        # Node styles
        for node_id, node in self.model.nodes.items():
            shape = {
                NodeKind.START: "circle",
                NodeKind.TASK: "box",
                NodeKind.DECISION: "diamond",
                NodeKind.END: "doublecircle",
            }.get(node.kind, "box")

            out.append(f'  "{node_id}" [shape={shape}, label="{node_id}"];')

        # Edges
        for e in self.model.edges:
            label = ""
            if e.kind == EdgeKind.ERROR:
                label = " [color=red]"
            out.append(f'  "{e.source}" -> "{e.target}"{label};')

        out.append("}")
        return "\n".join(out)
