# brain/research_entrypoint.py

from brain.c1.planner.intent_classifier import IntentClassifier
from brain.c1.planner.plan import Plan
from brain.c1.state import BrainState
from brain.build import build_brain


def run_research_episode(ticker: str, horizon: str = "swing", depth: str = "deep"):
    """
    High-level entrypoint for running a full E2-P3 research episode.
    Returns a structured research brief (Python dict or string).
    """

    # 1. Build the orchestrator (Brain-24)
    orchestrator = build_brain()   # <-- this IS the orchestrator

    # 2. Build initial state
    state = BrainState(
        user_input=f"research {ticker}",
        context={"ticker": ticker, "horizon": horizon, "depth": depth},
    )

    # 3. C1: classify intent
    classifier = IntentClassifier()
    intent = classifier.classify(None, state.user_input)

    # 4. C1: build plan
    plan = Plan.from_intent(
        intent=intent,
        params={"ticker": ticker, "horizon": horizon, "depth": depth},
    )

    # 5. C2: execute plan using the orchestrator
    result = orchestrator.run_with_plan(plan, state)

    # 6. Return final structured brief
    return result
