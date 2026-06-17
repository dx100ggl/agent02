# tests/c2/test_repair_planner_behavior.py

import pytest

from brain.c2.process_model import (
    ProcessModel,
    ProcessNode,
    NodeKind,
    EdgeKind,
)
from brain.c2.repair_planner import C2RepairPlanner


def test_repair_planner_inserts_repair_node_and_bypasses_failure():
    """
    End‑to‑end test of the repair planner.

    Scenario:
        A(start) → B(fails) → C(end)

    Expected after repair:
        A → B → repair_B → C
        B.handler is replaced with a no‑op
        repair_B runs and writes repair metadata into ctx
    """

    # --- failing handler ---
    def boom(ctx):
        raise RuntimeError("boom")

    # --- build model ---
    model = ProcessModel(id="test")
    model.add_node(ProcessNode(id="A", kind=NodeKind.START), is_start=True)
    model.add_node(ProcessNode(id="B", kind=NodeKind.TASK, handler=boom))
    model.add_node(ProcessNode(id="C", kind=NodeKind.END))

    model.add_edge("A", "B")
    model.add_edge("B", "C")

    # --- repair planner ---
    planner = C2RepairPlanner()

    # --- execution context ---
    ctx = {"steps": []}

    # --- run model with repair ---
    try:
        # This will raise inside B, triggering repair
        model = planner.repair_process_model(
            model=model,
            failing_node_id="B",
            ctx=ctx,
            error=RuntimeError("boom"),
        )
    except Exception:
        pytest.fail("repair_process_model should not re‑raise exceptions")

    # --- assertions ---

    # 1. repair node exists
    assert "repair_B" in model.nodes

    # 2. failing node handler is disabled
    assert model.nodes["B"].handler is not boom

    # 3. outgoing edges from B now go to repair_B
    outgoing_B = model.outgoing("B")
    assert len(outgoing_B) == 1
    assert outgoing_B[0].target == "repair_B"

    # 4. repair_B connects to original target C
    outgoing_repair = model.outgoing("repair_B")
    assert len(outgoing_repair) == 1
    assert outgoing_repair[0].target == "C"

    # 5. repair handler writes metadata
    repair_handler = model.nodes["repair_B"].handler
    repair_ctx = {}
    repair_handler(repair_ctx)

    assert repair_ctx["repair"]["node"] == "B"
    assert repair_ctx["repair"]["status"] == "repaired"
    assert "boom" in repair_ctx["repair"]["error"]
