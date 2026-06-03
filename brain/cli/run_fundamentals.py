# brain/cli/run_fundamentals.py
from __future__ import annotations

import argparse

from brain.llm.lmstudio_llm import LMStudioLLM
from brain.c1.planner.plan import build_fundamentals_plan
from brain.c2.executor.executor import PlanExecutor
from brain.c4.tools.registry import build_default_tool_registry
from brain.c4.synthesizer.synthesizer import ResearchSynthesizer


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run fundamentals-only research pipeline."
    )

    parser.add_argument("ticker", type=str, help="Ticker symbol (e.g. AAPL)")
    parser.add_argument(
        "--as-of",
        type=str,
        default=None,
        help="Optional as-of date (ISO format)",
    )
    parser.add_argument(
        "--intent",
        type=str,
        default="Fundamentals snapshot",
        help="Research intent string",
    )

    args = parser.parse_args()

    # ----------------------------------------------------------------------
    # LLM + Tools
    # ----------------------------------------------------------------------
    llm = LMStudioLLM()
    tools = build_default_tool_registry()

    # ----------------------------------------------------------------------
    # Build C1 plan
    # ----------------------------------------------------------------------
    plan = build_fundamentals_plan(
        ticker=args.ticker,
        intent=args.intent,
        as_of=args.as_of,
    )

    # ----------------------------------------------------------------------
    # Execute C2
    # ----------------------------------------------------------------------
    executor = PlanExecutor(llm=llm, tools=tools)
    exec_ctx = executor.execute(plan, ctx={})

    # ----------------------------------------------------------------------
    # Synthesize C4
    # ----------------------------------------------------------------------
    synthesizer = ResearchSynthesizer(llm=llm)
    report = synthesizer.synthesize_equity_research(
        ticker=args.ticker,
        intent=args.intent,
        exec_ctx=exec_ctx,
    )

    print("\n" + "=" * 80)
    print(report)
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
