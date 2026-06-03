from brain.research_entrypoint import ResearchEngine


def test_research_entrypoint_runs():
    engine = ResearchEngine()
    out = engine.run_research("research AAPL")

    assert "result" in out
    assert isinstance(out["result"], str)
