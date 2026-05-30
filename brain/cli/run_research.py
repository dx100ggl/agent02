# brain/cli/run_research.py

import argparse
from brain.research_entrypoint import run_research_episode
import json

def main():
    parser = argparse.ArgumentParser(description="Run Brain-24 research pipeline")
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--horizon", default="swing")
    parser.add_argument("--depth", default="deep")

    args = parser.parse_args()

    result = run_research_episode(
        ticker=args.ticker,
        horizon=args.horizon,
        depth=args.depth,
    )

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
