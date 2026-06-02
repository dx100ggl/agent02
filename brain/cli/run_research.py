# brain/cli/run_research.py

import sys

from brain.research_entrypoint import run_research


def _print_plan_summary(plan) -> None:
    if not plan or not getattr(plan, "steps", None):
        return

    print("=== PLAN (SUMMARY) ===")
    print(f"Steps: {len(plan.steps)}")
    for i, step in enumerate(plan.steps[:5]):
        desc = getattr(step, "description", "")
        tool = getattr(step, "tool", "")
        print(f"  {i+1}. {desc} [{tool}]")
    if len(plan.steps) > 5:
        print(f"  ... (+{len(plan.steps) - 5} more steps)")
    print()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m brain.cli.run_research \"your query here\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    result = run_research(query)

    print("=== QUERY ===")
    print(query)
    print()

    # Small, optional plan summary (no giant object dump)
    plan = result.get("plan")
    _print_plan_summary(plan)

    print("=== SYNTHESIS ===")
    print(result.get("synthesis", ""))
    print()

    print("=== REFLECTIONS ===")
    print(result.get("reflections", ""))
    print()


if __name__ == "__main__":
    main()
