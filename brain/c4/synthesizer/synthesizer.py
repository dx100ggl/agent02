# brain/c4/synthesizer/synthesizer.py

from __future__ import annotations
from typing import Any, Dict, List


class Synthesizer:
    """
    Multi‑section research synthesizer.
    Now belief‑aware (C5 → C4):
      - concise/detailed preferences
      - expert‑level tone for skill beliefs
      - shallow/normal reasoning depth
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
        beliefs: List[Any] | None = None,
    ) -> str:
        """
        Main synthesis entrypoint.
        Accepts normalized sections and produces a full research report.
        Beliefs optionally influence the prompt.
        """
        prompt = self._build_prompt(ticker, intent, sections, beliefs or [])
        raw = self.llm.run({"text": prompt})
        return self._extract_llm_text(raw)

    # ------------------------------------------------------------------
    # Prompt builder (now belief‑aware)
    # ------------------------------------------------------------------
    def _build_prompt(
        self,
        ticker: str,
        intent: str,
        sections: Dict[str, Any],
        beliefs: List[Any],
    ) -> str:

        # ---------------------------------------------------------
        # Belief‑aware modifiers
        # ---------------------------------------------------------
        prefix = ""

        # Concise preference
        if any(b.kind == "preference" and "concise" in b.metadata.get("tags", []) for b in beliefs):
            prefix += "Write the report in a concise, compact style.\n"

        # Detailed preference
        if any(b.kind == "preference" and "detailed" in b.metadata.get("tags", []) for b in beliefs):
            prefix += "Write the report with detailed explanations and expanded analysis.\n"

        # Skill → expert tone
        if any(b.kind == "skill" for b in beliefs):
            prefix += "Assume the reader is an expert; avoid basic explanations.\n"

        # Reasoning depth
        strong = [b for b in beliefs if getattr(b, "strength", 0) >= 0.8]
        if strong:
            prefix += "Use shallow reasoning and avoid long chains of inference.\n"

        # ---------------------------------------------------------
        # Base research prompt
        # ---------------------------------------------------------
        base = f"""
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

        return prefix + base

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

    # ------------------------------------------------------------------
    # Compatibility shim for old executor behavior
    # ------------------------------------------------------------------
    def synthesize(self, params: Dict[str, Any], exec_ctx: Dict[str, Any]) -> str:
        """
        Used when a SYNTHESIZE step is executed directly.
        Belief‑aware synthesis for generic LLM reasoning.
        """
        ticker = params.get("ticker", "UNKNOWN")
        intent = params.get("intent", "")

        beliefs = exec_ctx.get("beliefs", [])
        concise = any(b.kind == "preference" and "concise" in b.metadata.get("tags", []) for b in beliefs)
        detailed = any(b.kind == "preference" and "detailed" in b.metadata.get("tags", []) for b in beliefs)
        expert = any(b.kind == "skill" for b in beliefs)

        style = ""
        if concise:
            style = " (concise)"
        elif detailed:
            style = " (detailed)"
        elif expert:
            style = " (expert tone)"

        return f"Synthesis for {ticker}{style}: {intent}"
