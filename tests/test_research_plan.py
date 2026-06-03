from brain.c1.planner.plan import (
    build_full_research_plan,
    PlanStepKind,
)


def test_full_research_plan_structure():
    plan = build_full_research_plan("AAPL", "test intent")

    kinds = [step.kind for step in plan.steps]

    assert kinds == [
        PlanStepKind.MARKET_DATA,
        PlanStepKind.TECHNICALS,
        PlanStepKind.OPTIONS,
        PlanStepKind.SENTIMENT,
        PlanStepKind.MACRO,
        PlanStepKind.ANALOGS,
        PlanStepKind.FUNDAMENTALS,
        PlanStepKind.SYNTHESIZE,
    ]
