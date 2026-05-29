# tests/test_ch7_skill_learning.py

import pytest

from brain.build import build_brain
from brain.c1.state import State
from brain.c2.skill_learning.skill_trace import SkillTrace, TraceStep
from brain.c2.skill_learning.skill_store import SkillStore
from brain.c2.skill_learning.skill_learner import SkillLearner
from brain.c2.skill_learning.skill_retriever import SkillRetriever
from brain.c2.skill_learning.skill_router import SkillRouter


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def make_trace(task_id: str, actions: list[str]):
    return SkillTrace(
        task_id=task_id,
        steps=[
            TraceStep(action=a, params={"x": 1}, result=None)
            for a in actions
        ],
    )


# ---------------------------------------------------------
# Ch7-1: SkillStore basic persistence
# ---------------------------------------------------------

def test_ch7_skill_store_persistence():
    brain = build_brain()
    memory = brain.memory

    store = SkillStore(memory)

    trace = make_trace("t1", ["a", "b"])
    learner = SkillLearner(memory)

    # Learn from repeated pattern
    learned = learner.learn_from_traces([trace, trace])
    assert len(learned) == 1

    record = learned[0]
    loaded = store.get(record.signature.name)

    assert loaded is not None
    assert loaded.signature.name == record.signature.name
    assert loaded.policy.steps[0].action == "a"
    assert loaded.policy.steps[1].action == "b"


# ---------------------------------------------------------
# Ch7-2: SkillLearner learns repeated patterns only
# ---------------------------------------------------------

def test_ch7_skill_learner_detects_repetition():
    brain = build_brain()
    memory = brain.memory

    learner = SkillLearner(memory)

    t1 = make_trace("taskA", ["x", "y"])
    t2 = make_trace("taskA", ["x", "y"])

    learned = learner.learn_from_traces([t1, t2])
    assert len(learned) == 1

    t3 = make_trace("taskB", ["x", "z"])
    learned2 = learner.learn_from_traces([t3])
    assert len(learned2) == 0


# ---------------------------------------------------------
# Ch7-3: SkillRetriever finds matching skills
# ---------------------------------------------------------

def test_ch7_skill_retriever_matches_description():
    brain = build_brain()
    memory = brain.memory

    learner = SkillLearner(memory)
    store = SkillStore(memory)
    retriever = SkillRetriever(store)

    t1 = make_trace("email_task", ["compose", "send"])
    learner.learn_from_traces([t1, t1])

    skill = retriever.find_matching_skill("please auto-learned skill for email")
    assert skill is not None
    assert "auto-learned" in skill.signature.description.lower()


# ---------------------------------------------------------
# Ch7-4: SkillRouter executes a learned skill
# ---------------------------------------------------------

class DummyPlanner:
    def __init__(self):
        self.calls = []

    def execute(self, action, params):
        self.calls.append((action, params))
        return f"done:{action}"


def test_ch7_skill_router_executes_skill():
    brain = build_brain()
    memory = brain.memory

    learner = SkillLearner(memory)
    store = SkillStore(memory)

    t1 = make_trace("math_task", ["add", "multiply"])
    learner.learn_from_traces([t1, t1])

    planner = DummyPlanner()
    router = SkillRouter(store=store, planner=planner)

    result = router.route("please auto-learned skill for math")
    assert result == "done:multiply"
    assert planner.calls == [
        ("add", {"x": 1}),
        ("multiply", {"x": 1}),
    ]


# ---------------------------------------------------------
# Ch7-5: Orchestrator uses skill routing before planning
# ---------------------------------------------------------

def test_ch7_orchestrator_skill_routing_shortcuts_planning():
    brain = build_brain()
    memory = brain.memory

    learner = brain.skill_learner
    t1 = make_trace("shortcut_task", ["step1", "step2"])
    learner.learn_from_traces([t1, t1])

    state = State("please auto-learned skill for shortcut")
    output = brain.run(state)

    assert output is not None


# ---------------------------------------------------------
# Ch7-6: Orchestrator logs traces for learning
# ---------------------------------------------------------

def test_ch7_orchestrator_learns_from_execution_trace():
    brain = build_brain()
    memory = brain.memory

    state = State("hello world")
    brain.run(state)

    store = SkillStore(memory)
    all_skills = store.load_all()

    assert isinstance(all_skills, dict)
