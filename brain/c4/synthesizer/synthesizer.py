# brain/c4/synthesizer/synthesizer.py

from brain.c1.state import BrainState

class Synthesizer:
    def __init__(self, llm=None):
        self.llm = llm

    def synthesize(self, state: BrainState):
        # 1. Check for research sections
        if hasattr(state, "meta") and isinstance(state.meta, dict):
            sections = state.meta.get("research_sections")
            ticker = state.meta.get("ticker", "UNKNOWN")

            if sections and self.llm:
                prompt = f"""
You are Brain-24, a financial research engine.

Write a structured deep-dive swing-horizon (1–4 weeks) research brief for {ticker}.

User priorities (in order): Technical, Sentiment, Macro, Fundamentals, Catalysts.
Include full options-market context and 3-year historical analogs.

[TECHNICAL / MARKET DATA]
{sections.get("technical")}

[OPTIONS]
{sections.get("options")}

[SENTIMENT]
{sections.get("sentiment")}

[MACRO / SECTOR]
{sections.get("macro")}

[HISTORICAL ANALOGS]
{sections.get("analogs")}

Write a structured brief with sections:
1) Current technical regime
2) Options market and volatility context
3) Sentiment and narrative
4) Macro and sector overlay
5) Historical analogs (last 3 years)
6) 1–4 week scenarios: bull / base / bear
7) Key levels, triggers, and invalidations
"""

                raw = self.llm.run({"text": prompt})
                
                # --- UNIVERSAL EXTRACTION LOGIC ---
                if isinstance(raw, dict):

                    # LM Studio / OpenAI chat completion
                    if "choices" in raw and raw["choices"]:
                        msg = raw["choices"][0].get("message", {})
                        if "content" in msg:
                            return msg["content"]

                    # Legacy formats
                    return (
                        raw.get("text")
                        or raw.get("output")
                        or raw.get("response")
                        or raw.get("answer")
                        or ""
                    )

                # Fallback
                return str(raw)

        # 2. Fallback to last tool result
        return state.history[-1]["result"] if state.history else ""
