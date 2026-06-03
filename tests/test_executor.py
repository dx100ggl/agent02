from brain.c2.executor.executor import Executor
from brain.c4.tools.registry import ToolRegistry
from brain.c4.synthesizer.synthesizer import Synthesizer
from brain.llm.lmstudio_llm import LMStudioLLM
from brain.c1.planner.plan import (
    ResearchPlan,
    PlanStep,
    PlanStepKind,
)


def test_executor_runs_single_step():
    tools = ToolRegistry()
    llm = LMStudioLLM()
    synth = Synthesizer(llm)
    executor = Executor(tools=tools, synthesizer=synth, llm=llm)

    plan = ResearchPlan(
        steps=[
            PlanStep(
                kind=PlanStepKind.SYNTHESIZE,
                tool_name=None,
                params={"ticker": "AAPL", "intent": "test"},
            )
        ]
    )

    ctx = executor.execute(plan, ctx={})
    assert "final" in ctx
