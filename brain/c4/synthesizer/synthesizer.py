from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List

# Belief modifiers (new modular file)
from .modifiers import BeliefModifiers, normalize_beliefs


# ================================================================
# Research sections (stable schema)
# ================================================================

@dataclass(frozen=True)
class ResearchSections:
    market: str
    technicals: str
    options: str
    sentiment: str
    macro: str
    analogs: str
    fundamentals: str

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ResearchSections":
        # Deterministic fallback to empty string
        return ResearchSections(
            market=str(d.get("market", "")),
            technicals=str(d.get("technicals", "")),
            options=str(d.get("options", "")),
            sentiment=str(d.get("sentiment", "")),
            macro=str(d.get("macro", "")),
            analogs=str(d.get("analogs", "")),
            fundamentals=str(d.get("fundamentals", "")),
        )


# ================================================================
# Stabilized Synthesizer
# ================================================================

class Synthesizer:
    """
    Stabilized multi‑section research synthesizer.
    Deterministic, belief‑aware, schema‑validated.
    """

    def __init__(self, llm: Any):
        self.llm = llm

    # --------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------
    def synthesize_from_sections(
        self,
        ticker: str,
        intent: str,
        sections: Dict[str, Any],
        beliefs: List[Any] | None = None,
    ) -> str:

        mods = normalize_beliefs(beliefs or [])
        sec = ResearchSections.from_dict(sections)

        prompt = self._build_prompt(ticker, intent, sec, mods)
        raw = self.llm.run({"text": prompt})

        return self._extract_llm_text(raw)

    # --------------------------------------------------------------
    # Deterministic prompt builder
    # --------------------------------------------------------------
    def _build_prompt(
        self,
        ticker: str,
        intent: str,
        sec: ResearchSections,
        mods: BeliefModifiers,
    ) -> str:

        prefix_lines = []

        if mods.concise:
            prefix_lines.append("Write the report in a concise, compact style.")
        if mods.detailed:
            prefix_lines.append("Write the report with detailed explanations and expanded analysis.")
        if mods.expert:
            prefix_lines.append("Assume the reader is an expert; avoid basic explanations.")
        if mods.shallow_reasoning:
            prefix_lines.append("Use shallow reasoning and avoid long chains of inference.")

        prefix = "\n".join(prefix_lines)

        base = f"""
You are Brain‑24, a multi‑tool equity research engine.

Write a full, structured research report for {ticker}.
User intent: {intent}

Below are normalized research sections from multiple tools:

===========================
[MARKET]
{sec.market}

[TECHNICALS]
{sec.technicals}

[OPTIONS]
{sec.options}

[SENTIMENT]
{sec.sentiment}

[MACRO]
{sec.macro}

[ANALOGS]
{sec.analogs}

[FUNDAMENTALS]
{sec.fundamentals}
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

        return prefix + "\n" + base

    # --------------------------------------------------------------
    # Strict LM response extraction
    # --------------------------------------------------------------
    def _extract_llm_text(self, raw: Any) -> str:
        if isinstance(raw, dict):
            # LM Studio chat format
            if "choices" in raw:
                choices = raw["choices"]
                if isinstance(choices, list) and choices:
                    msg = choices[0].get("message", {})
                    content = msg.get("content")
                    if isinstance(content, str):
                        return content
                raise ValueError("Malformed LLM response: missing choices/message/content")

            # No silent fallback — enforce explicit schema
            raise ValueError("Malformed LLM response: expected chat-completion format")

        # Non-dict → treat as plain text
        return str(raw)

    # --------------------------------------------------------------
    # Legacy compatibility shim
    # --------------------------------------------------------------
    def synthesize(self, params: Dict[str, Any], exec_ctx: Dict[str, Any]) -> str:
        ticker = params.get("ticker", "UNKNOWN")
        intent = params.get("intent", "")

        mods = normalize_beliefs(exec_ctx.get("beliefs", []))

        if mods.concise:
            style = " (concise)"
        elif mods.detailed:
            style = " (detailed)"
        elif mods.expert:
            style = " (expert tone)"
        else:
            style = ""

        return f"Synthesis for {ticker}{style}: {intent}"
