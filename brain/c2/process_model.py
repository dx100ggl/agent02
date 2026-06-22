# brain/c2/process_model.py

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

        import logging
        self._log = logging.getLogger(__name__)

    def run(self, ctx: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ctx = ctx or {}
        current = self.model.start_node_id

        self._log.debug(f"[PROCESS] Starting ProcessModel: {self.model.id}")
        self._log.debug(f"[PROCESS] Start node: {current}")

        while True:
            node = self.model.nodes[current]
            self._log.debug(f"[NODE] Entering node: {node.id} ({node.kind.name})")

            # -----------------------------------------------------
            # C6: BEFORE NODE HOOK
            # -----------------------------------------------------
            if self.meta:
                directive = self.meta.before_node(node, ctx)
                if directive:
                    self._log.debug(f"[META] before_node directive: {directive}")
                    current = self._apply_directive(directive, node, ctx)
                    if current is None:
                        self._log.debug("[META] Directive ended execution")
                        return ctx
                    continue

            # Execute node
            try:
                self._log.debug(f"[EXEC] Running handler for node {node.id}")
                node.run(ctx)
            except Exception as e:
                setattr(e, "node_id", node.id)
                self._log.exception(f"[ERROR] Exception in node {node.id}")
                raise

            # END node
            if node.kind == NodeKind.END:
                self._log.debug(f"[END] Reached END node: {node.id}")
                return ctx

            # -----------------------------------------------------
            # C6: AFTER NODE HOOK
            # -----------------------------------------------------
            if self.meta:
                directive = self.meta.after_node(node, ctx)
                if directive:
                    self._log.debug(f"[META] after_node directive: {directive}")
                    current = self._apply_directive(directive, node, ctx)
                    if current is None:
                        self._log.debug("[META] Directive ended execution")
                        return ctx
                    continue

            # Normal transition
            edges = self.model.outgoing(current)

            if node.kind == NodeKind.DECISION:
                chosen = None
                for e in edges:
                    cond_ok = (e.condition is None or e.condition(ctx))
                    self._log.debug(
                        f"[DECISION] Edge {node.id} → {e.target} "
                        f"(condition={e.condition}, result={cond_ok})"
                    )
                    if cond_ok:
                        chosen = e
                        break

                if chosen is None:
                    raise RuntimeError(f"No valid decision edge from node {current}")

                self._log.debug(
                    f"[TRANSITION] DECISION: {node.id} → {chosen.target}"
                )
                current = chosen.target

            else:
                normal_edges = [e for e in edges if e.kind == EdgeKind.NORMAL]

                if len(normal_edges) != 1:
                    raise RuntimeError(f"Ambiguous or missing next step from {current}")

                next_id = normal_edges[0].target
                self._log.debug(
                    f"[TRANSITION] NORMAL: {node.id} → {next_id}"
                )
                current = next_id

        return ctx

    # ---------------------------------------------------------
    # Directive handler
    # ---------------------------------------------------------
    def _apply_directive(self, directive, node, ctx):
        action = directive.get("action")
        self._log.debug(f"[DIRECTIVE] Applying {action} on node {node.id}")

        if action == "skip":
            edges = self.model.outgoing(node.id)
            normal = [e for e in edges if e.kind == EdgeKind.NORMAL]
            target = normal[0].target if normal else None
            self._log.debug(f"[DIRECTIVE] skip → {target}")
            return target

        if action == "goto":
            target = directive["target"]
            self._log.debug(f"[DIRECTIVE] goto → {target}")
            return target

        if action == "insert_after":
            new_node = directive["node"]
            self.model.add_node(new_node)
            edges = self.model.outgoing(node.id)

            for e in edges:
                e.source = new_node.id

            self.model.add_edge(node.id, new_node.id)
            self._log.debug(f"[DIRECTIVE] insert_after → {new_node.id}")
            return new_node.id

        if action == "replace_handler":
            node.handler = directive["handler"]
            self._log.debug(f"[DIRECTIVE] replace_handler on {node.id}")
            return node.id

        self._log.debug(f"[DIRECTIVE] No-op directive on {node.id}")
        return node.id
