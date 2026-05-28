# tests/test_s4_skill_integration.py

from __future__ import annotations

from brain.build import build_brain
from brain.c2.skill_learning.skill_trace import SkillTrace, TraceStep
from brain.c2.skill_learning.skill_types import SkillRecord


def test_s4_skill_learning_roundtrip():
    brain = build_brain(use_lmstudio=False)

    # Ensure orchestrator has skill_learner and skill_router
    assert getattr(brain, "skill_learner", None) is not None
    assert getattr(brain, "skill_router", None) is not None

    learner = brain.skill_learner

    # Build a simple trace with repeated pattern
    trace = SkillTrace(
        task_id="s4_skill_test",
        steps=[
            TraceStep(action="use_tool", params={"tool": "search_memory", "args": {"query": "foo"}}, result=None),
            TraceStep(action="use_tool", params={"tool": "search_memory", "args": {"query": "foo"}}, result=None),
        ],
    )

    learned = learner.learn_from_traces([trace])
    assert isinstance(learned, list)

    if learned:
        record: SkillRecord = learned[0]
        assert record.signature.name
        assert record.policy.steps


def test_s4_skill_router_no_skill_fallback():
    brain = build_brain(use_lmstudio=False)
    router = brain.skill_router

    # No skills yet for this description → should return None
    result = router.route("some completely new task description")
    assert result is None
