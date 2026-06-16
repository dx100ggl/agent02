from brain.c2.process_model import ProcessModel, ProcessNode, NodeKind, ProcessRunner
from brain.c2.repair_planner import C2RepairPlanner

def test_repair_fires_on_failure():
    def boom(ctx):
        raise RuntimeError("boom")

    model = ProcessModel(id="test")
    model.add_node(ProcessNode(id="start", kind=NodeKind.START), is_start=True)
    model.add_node(ProcessNode(id="fail", kind=NodeKind.TASK, handler=boom))
    model.add_node(ProcessNode(id="end", kind=NodeKind.END))

    model.add_edge("start", "fail")
    model.add_edge("fail", "end")

    repair = C2RepairPlanner()

    ctx = {"steps": []}

    attempts = 0
    while True:
        try:
            runner = ProcessRunner(model)
            runner.run(ctx)
            break
        except Exception as e:
            attempts += 1
            assert attempts <= 1, "repair should resolve in one attempt"
            assert getattr(e, "node_id", None) == "fail"
            model = repair.repair_process_model(
                model=model,
                failing_node_id=e.node_id,
                ctx=ctx,
                error=e,
            )

    # after repair, model should contain a repair node
    assert any(n.startswith("repair_fail") for n in model.nodes)
