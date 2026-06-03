from brain.c4.synthesizer.synthesizer import Synthesizer
from brain.llm.lmstudio_llm import LMStudioLLM


def test_synthesizer_runs():
    llm = LMStudioLLM()
    synth = Synthesizer(llm)

    sections = {
        "market": {"trend": "up"},
        "technicals": {"momentum": "strong"},
        "options": {"iv_rank": 20},
        "sentiment": {"news_sentiment": "neutral"},
        "macro": {"rates": "stable"},
        "analogs": {"closest_match": "MSFT"},
        "fundamentals": {"growth": {"revenue_yoy": 10}},
    }

    out = synth.synthesize_from_sections(
        ticker="AAPL",
        intent="test intent",
        sections=sections,
    )

    assert isinstance(out, str)
    assert "AAPL" in out
