# brain/research_entrypoint.py

from brain.c1.planner.intent_classifier import classify_intent
from brain.c1.planner.plan import Plan
from brain.c2.meta_controller import MetaController
from brain.c1.state import BrainState

def run_research_episode(ticker: str, horizon: str = "swing", depth: str = "deep"):
    """
    High-level entrypoint for running a full E2-P3 research episode.
    Returns a structured research brief (Python dict).
    """

    # 1. Build initial state
    state = BrainState(
        user_input=f"research {ticker}",
        context={"ticker": ticker, "horizon": horizon, "depth": depth},
    )

    # 2. C1: classify intent
    intent = classify_intent(state.user_input)

    # 3. C1: build plan
    plan = Plan.from_intent(
        intent=intent,
        params={"ticker": ticker, "horizon": horizon, "depth": depth},
    )

    # 4. C2: execute plan
    controller = MetaController()
    result = controller.execute(plan, state)

    # 5. Return final structured brief
    return result.output
