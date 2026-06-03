# brain/c4/synthesizer/synthesizer.py

from __future__ import annotations
from typing import Any, Dict

from brain.c1.state import BrainState


class Synthesizer:
    """
    Multi‑section research synthesizer.
    Consumes:
        state.meta["research_sections"] = {
            "market": {...},
            "technicals": {...},
            "options": {...},
            "sentiment": {...},
            "macro": {...},
            "analogs": {...},
            "fundamentals": {...},
        }

    Produces:
        A structured multi‑section research report.
    """

    def __init__(self, llm=None):
        self.llm = llm

    # ------------------------------------------------------------------
    # Main entrypoint
    # ------------------------------------------------------------------
    def synthesize(self, state: BrainState) -> str:
        if not self.llm:
            return "No LLM configured for synthesis."

        sections = state.meta.get("research_sections", {})
        ticker = state.meta.get("ticker", "UNKNOWN")

        # Build the prompt
        prompt = f"""
You are Brain‑24, a multi‑tool equity research engine.

Write a full, structured research report for {ticker} using the sections below.
Each section may contain raw tool outputs, summaries, or partial data.
Your job is to integrate them into a coherent 1–4 week swing‑horizon research note.

User intent: {state.user_input}

===========================
[MARKET DATA]
{sections.get("market", {})}

[TECHNICALS]
{sections.get("technicals", {})}

[OPTIONS]
{sections.get("options", {})}

[SENTIMENT]
{sections.get("sentiment", {})}

[MACRO]
{sections.get("macro", {})}

[ANALOGS]
{sections.get("analogs", {})}

[FUNDAMENTALS]
{sections.get("fundamentals", {})}
===========================

Write a structured research report with the following sections:

1) Market regime overview  
2) Technical structure and key levels  
3) Options market and volatility context  
4) Sentiment and narrative  
5) Macro and sector overlay  
6) Historical analogs (1–3 year lookback)  
7) Fundamentals snapshot  
8) 1–4 week scenarios (bull / base / bear)  
9) Key levels, triggers, and invalidations  
10) Final synthesis and risk summary

Be concise, analytical, and avoid repetition.
"""

        raw = self.llm.run({"text": prompt})

        # Extract text from LM Studio response
        if isinstance(raw, dict):
            # Chat completion format
            if "choices" in raw and raw["choices"]:
                msg = raw["choices"][0].get("message", {})
                if "content" in msg:
                    return msg["content"]

            # Legacy formats
            return (
                raw.get("answer")
                or raw.get("LLM")
                or raw.get("text")
                or raw.get("output")
                or raw.get("response")
                or ""
            )

        return str(raw)
