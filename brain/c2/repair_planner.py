# brain/c2/repair_planner.py

from typing import Dict, Any, Optional, List
from datetime import datetime

from brain.c2.process_model import (
    ProcessModel,
    ProcessNode,
    NodeKind,
    EdgeKind,
)


class C2RepairPlanner:
    def repair(self, plan):
        return {
            "repaired": False,
            "notes": "No repair applied (stub)."
        }

    # ---------------------------------------------------------
    # ProcessModel repair entrypoint
    # ---------------------------------------------------------
    def repair_process_model(
        self,
        model: ProcessModel,
        failing_node_id: str,
        ctx: Dict[str, Any],
        error: Exception,
    ) -> ProcessModel:
        # Initialize repair log
        ctx.setdefault("repair_log", [])
        ctx["repair_log"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "repair_started",
            "failing_node": failing_node_id,
            "error": str(error),
        })

        """
        Default repair strategy:
          - Insert a repair node immediately after the failing node.
          - Disable the failing node so it cannot throw again.
          - Reroute outgoing edges through the repair node.
        """

        repair_node_id = f"repair_{failing_node_id}"

        def repair_handler(c):
            c["repair"] = {
                "node": failing_node_id,
                "error": str(error),
                "status": "repaired",
            }

        repair_node = ProcessNode(
            id=repair_node_id,
            kind=NodeKind.TASK,
            handler=repair_handler,
        )

        # Add repair node
        model.add_node(repair_node)

        # Disable failing node so it won't throw again
        model.nodes[failing_node_id].handler = lambda c: None

        # Capture outgoing edges from failing node
        outgoing = model.outgoing(failing_node_id)

        # Remove edges OUT OF failing node
        model.edges = [
            e for e in model.edges
            if e.source != failing_node_id
        ]

        # Insert new edge: failing_node -> repair_node
        model.add_edge(
            failing_node_id,
            repair_node_id,
            kind=EdgeKind.NORMAL,
        )

        # Log repair node insertion
        ctx["repair_log"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "inserted_repair_node",
            "repair_node": repair_node_id,
        })

        # Reconnect repair_node to original targets
        for e in outgoing:
            model.add_edge(
                repair_node_id,
                e.target,
                kind=e.kind,
                condition=e.condition,
            )

        # Log reconnection
        ctx["repair_log"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "reconnected_edges",
            "repair_node": repair_node_id,
            "targets": [e.target for e in outgoing],
        })

        return model
