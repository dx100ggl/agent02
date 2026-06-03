# brain/c4/synthesizer/synthesizer.py

from __future__ import annotations
from typing import Any, Dict


class Synthesizer:
    """
    Multi‑section research synthesizer.
    Consumes normalized sections from SectionNormalizer and produces
    a structured, LLM‑generated research report.
    """

    def __init__(self, llm: Any):
        self.llm = llm

    # ------------------------------------------------------------------
    # Public API used by ResearchEngine
    # ------------------------------------------------------------------
    def synthesize_from_sections(
        self,
        ticker: str,
        intent: str,
        sections: Dict[str, Any],
    ) -> str:
        """
        Main synthesis entrypoint.
        Accepts normalized sections and produces a full research report.
        """
        prompt = self._build_prompt(ticker, intent, sections)
        raw = self.llm.run({"text": prompt})
        return self._extract_llm_text(raw)

    # ------------------------------------------------------------------
    # Prompt builder
    # ------------------------------------------------------------------
    def _build_prompt(
        self,
        ticker: str,
        intent: str,
        sections: Dict[str, Any],
    ) -> str:

        return f"""
You are Brain‑24, a multi‑tool equity research engine.

Write a full, structured research report for {ticker}.
User intent: {intent}

Below are normalized research sections from multiple tools:

===========================
[MARKET]
{sections.get("market")}

[TECHNICALS]
{sections.get("technicals")}

[OPTIONS]
{sections.get("options")}

[SENTIMENT]
{sections.get("sentiment")}

[MACRO]
{sections.get("macro")}

[ANALOGS]
{sections.get("analogs")}

[FUNDAMENTALS]
{sections.get("fundamentals")}
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

Guidelines:
- Be concise, analytical, and avoid repetition.
- Integrate signals across sections.
- Use professional equity‑research tone.
- Do not hallucinate data not implied by the sections.
"""

    # ------------------------------------------------------------------
    # Extract text from LM Studio response
    # ------------------------------------------------------------------
    def _extract_llm_text(self, raw: Any) -> str:
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

    def synthesize(self, params: Dict[str, Any], exec_ctx: Dict[str, Any]) -> str:
        """
        Compatibility shim for old executor behavior.
        Used when a SYNTHESIZE step is executed directly.
        """
        ticker = params.get("ticker", "UNKNOWN")
        intent = params.get("intent", "")
        return f"Synthesis for {ticker}: {intent}"
