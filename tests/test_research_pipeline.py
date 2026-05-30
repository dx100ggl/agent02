# tests/test_research_pipeline.py

import pytest

from brain.c1.planner.intent_classifier import IntentClassifier
from brain.c1.planner.plan import build_plan_for_intent
from brain.c4.tools.registry import ToolRegistry
from brain.c2.executor.executor import Executor

from brain.c2.skill_learning.research_skill import ResearchSkill
from brain.c4.synthesizer.synthesizer import Synthesizer

from tests.helpers.fake_llm import FakeLLM
from tests.helpers.fake_memory import FakeMemory
from tests.helpers.fake_state import FakeState


# ---------------------------------------------------------
# End‑to‑end test: NVDA research pipeline
# ---------------------------------------------------------
def test_research_pipeline_end_to_end():
    user_input = "Generate a deep-dive swing research brief for NVDA"

    # 1. Intent classification
    llm = FakeLLM()
    classifier = IntentClassifier()
    intent_name = classifier.classify(llm, user_input)
    assert intent_name == "equity_research"

    # 2. Build plan
    plan = build_plan_for_intent(intent_name, user_input, ticker="NVDA")
    assert len(plan.steps) == 5

    # 3. Build state
    memory = FakeMemory()
    state = FakeState(user_input=user_input, memory=memory)
    state.meta["intent"] = intent_name

    # 4. Tools + executor
    tools = ToolRegistry()
    executor = Executor(tools, memory)

    executor.execute_plan(plan, state)

    # All steps should have results
    for step in plan.steps:
        assert step.result is not None
        assert isinstance(step.result, dict)

    # 5. ResearchSkill aggregation
    step_results = {
        step.description.lower().replace(" ", "_"): step.result
        for step in plan.steps
    }

    skill = ResearchSkill()
    sections = skill.run(step_results, state)

    assert "technical" in sections
    assert "options" in sections
    assert "sentiment" in sections
    assert "macro" in sections
    assert "analogs" in sections

    # 6. Synthesizer
    synth = Synthesizer(llm)
    output = synth.synthesize(state)

    assert isinstance(output, str)
    assert "NVDA" in output
    assert "technical" in output.lower()
    assert "options" in output.lower()
    assert "sentiment" in output.lower()
    assert "macro" in output.lower()
    assert "analog" in output.lower()

    # 7. Final success
    print("\n=== FINAL RESEARCH BRIEF ===\n")
    print(output)
