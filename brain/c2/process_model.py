from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional


# ============================================================
# Node / Edge Types
# ============================================================

class NodeKind(Enum):
    START = auto()
    TASK = auto()
    DECISION = auto()
    END = auto()


class EdgeKind(Enum):
    NORMAL = auto()
    ERROR = auto()


# ============================================================
# Core Data Structures
# ============================================================

@dataclass
class ProcessEdge:
    source: str
    target: str
    kind: EdgeKind = EdgeKind.NORMAL
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None


@dataclass
class ProcessNode:
    id: str
    kind: NodeKind
    handler: Optional[Callable[[Dict[str, Any]], None]] = None

    def run(self, ctx: Dict[str, Any]) -> None:
        if self.handler is not None:
            self.handler(ctx)


@dataclass
class ProcessModel:
    """
    Declarative process graph used by the C2 orchestrator.

    - nodes: mapping of node_id → ProcessNode
    - edges: list of directed edges
    - start_node_id: entry point for execution
    """
    id: str
    nodes: Dict[str, ProcessNode] = field(default_factory=dict)
    edges: List[ProcessEdge] = field(default_factory=list)
    start_node_id: Optional[str] = None

    # -----------------------------
    # Node / Edge Construction
    # -----------------------------

    def add_node(self, node: ProcessNode, is_start: bool = False) -> None:
        if node.id in self.nodes:
            raise ValueError(f"Node {node.id} already exists")

        self.nodes[node.id] = node

        if is_start or self.start_node_id is None:
            self.start_node_id = node.id

    def add_edge(
        self,
        source: str,
        target: str,
        kind: EdgeKind = EdgeKind.NORMAL,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> None:
        if source not in self.nodes:
            raise ValueError(f"Source node {source} does not exist")
        if target not in self.nodes:
            raise ValueError(f"Target node {target} does not exist")

        self.edges.append(
            ProcessEdge(
                source=source,
                target=target,
                kind=kind,
                condition=condition,
            )
        )

    # -----------------------------
    # Query Helpers
    # -----------------------------

    def outgoing(self, node_id: str) -> List[ProcessEdge]:
        return [e for e in self.edges if e.source == node_id]


# ============================================================
# Process Runner
# ============================================================

class ProcessRunner:
    """
    Executes a ProcessModel by walking its directed graph.

    Supports optional meta-controller hooks:
      - before_node(node, ctx) → directive
      - after_node(node, ctx)  → directive
    """

    def __init__(self, model: ProcessModel, meta_controller=None):
        if model.start_node_id is None:
            raise ValueError("ProcessModel must define a start node")
        self.model = model
        self.meta = meta_controller

    def run(self, ctx: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ctx = ctx or {}
        current = self.model.start_node_id

        while True:
            node = self.model.nodes[current]

            # -----------------------------------------------------
            # C6: BEFORE NODE HOOK
            # -----------------------------------------------------
            if self.meta:
                directive = self.meta.before_node(node, ctx)
                if directive:
                    current = self._apply_directive(directive, node, ctx)
                    if current is None:
                        return ctx
                    continue

            # Execute node
            try:
                node.run(ctx)
            except Exception as e:
                # Attach failing node id for repair logic
                setattr(e, "node_id", node.id)
                raise

            # END node
            if node.kind == NodeKind.END:
                return ctx

            # -----------------------------------------------------
            # C6: AFTER NODE HOOK
            # -----------------------------------------------------
            if self.meta:
                directive = self.meta.after_node(node, ctx)
                if directive:
                    current = self._apply_directive(directive, node, ctx)
                    if current is None:
                        return ctx
                    continue

            # Normal transition
            edges = self.model.outgoing(current)

            if node.kind == NodeKind.DECISION:
                chosen = None
                for e in edges:
                    if e.condition is None or e.condition(ctx):
                        chosen = e
                        break
                if chosen is None:
                    raise RuntimeError(f"No valid decision edge from node {current}")
                current = chosen.target
            else:
                normal_edges = [e for e in edges if e.kind == EdgeKind.NORMAL]
                if len(normal_edges) != 1:
                    raise RuntimeError(f"Ambiguous or missing next step from {current}")
                current = normal_edges[0].target

        return ctx

    # ---------------------------------------------------------
    # Directive handler
    # ---------------------------------------------------------
    def _apply_directive(self, directive, node, ctx):
        """
        Supported directives:
          {"action": "skip"}
          {"action": "goto", "target": "node_id"}
          {"action": "insert_after", "node": ProcessNode}
          {"action": "replace_handler", "handler": fn}
        """

        action = directive.get("action")

        if action == "skip":
            # Move to next node without running this one
            edges = self.model.outgoing(node.id)
            normal = [e for e in edges if e.kind == EdgeKind.NORMAL]
            return normal[0].target if normal else None

        if action == "goto":
            return directive["target"]

        if action == "insert_after":
            new_node = directive["node"]
            self.model.add_node(new_node)
            # reroute edges
            edges = self.model.outgoing(node.id)
            for e in edges:
                e.source = new_node.id
            self.model.add_edge(node.id, new_node.id)
            return new_node.id

        if action == "replace_handler":
            node.handler = directive["handler"]
            return node.id

        return node.id
