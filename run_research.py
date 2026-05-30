# run_research.py

from brain.c1.planner.intent_classifier import IntentClassifier
from brain.c1.planner.plan import build_plan_for_intent
from brain.c1.state import State

from brain.c4.tools.registry import ToolRegistry
from brain.c2.executor.executor import Executor

from brain.c2.skill_learning.research_skill import ResearchSkill
from brain.c4.synthesizer.synthesizer import Synthesizer

from brain.llm.lmstudio_llm import LMStudioLLM


def run_research(user_input: str, ticker: str = "NVDA") -> str:
    """
    End‑to‑end Brain‑24 research pipeline:
    - Intent classification
    - Research plan construction
    - Tool execution
    - ResearchSkill aggregation
    - Synthesizer (LLM) final brief
    """

    # 1. Intent classification
    llm = LMStudioLLM()
    classifier = IntentClassifier()

    # IntentClassifier expects a callable(prompt)->str
    def _llm(prompt: str) -> str:
        raw = llm.run({"text": prompt})
        if isinstance(raw, dict):
            return raw.get("text") or raw.get("output") or raw.get("response") or ""
        return str(raw)

    intent_name = classifier.classify(_llm, user_input)

    # 2. Build research plan
    plan = build_plan_for_intent(intent_name, user_input, ticker)

    # 3. Build state
    state = State(user_input=user_input)
    state.meta = {"intent": intent_name}

    # 4. Tools + executor
    tools = ToolRegistry()
    executor = Executor(tools=tools, memory=state.memory)

    executor.execute_plan(plan, state)

    # 5. Aggregate tool outputs into research sections
    step_results = {
        step.description.lower().replace(" ", "_"): step.result
        for step in plan.steps
    }

    skill = ResearchSkill()
    skill.run(step_results, state)

    # 6. Synthesize final research brief
    synth = Synthesizer(llm)
    output = synth.synthesize(state)

    return output


if __name__ == "__main__":
    text = "Generate a deep-dive swing research brief for NVDA"
    print(run_research(text))
