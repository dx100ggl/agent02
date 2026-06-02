# brain/c4/synthesizer/synthesizer.py

from typing import Any, Dict, List
from brain.c1.state import BrainState


class Synthesizer:
    def __init__(self, llm=None):
        self.llm = llm

    # ---------------------------------------------------------
    # Helpers: summarization utilities
    # ---------------------------------------------------------
    def _summarize_technical(self, technical: Dict) -> Dict:
        ohlcv = technical.get("ohlcv", [])
        if not ohlcv:
            return {}

        closes = [row["Close"] for row in ohlcv[-20:]]  # last 20 days
        trend = "uptrend" if closes[-1] > closes[0] else "downtrend"

        return {
            "ticker": technical.get("ticker"),
            "trend": trend,
            "recent_high": max(closes),
            "recent_low": min(closes),
            "last_close": closes[-1],
        }

    def _summarize_options(self, options: Dict) -> Dict:
        if not options:
            return {}

        return {
            "iv": options.get("iv"),
            "iv_rank": options.get("iv_rank"),
            "iv_percentile": options.get("iv_percentile"),
            "delta": options.get("greeks", {}).get("delta"),
            "gamma": options.get("greeks", {}).get("gamma"),
            "theta": options.get("greeks", {}).get("theta"),
            "vega": options.get("greeks", {}).get("vega"),
        }

    def _summarize_sentiment(self, sentiment: Dict) -> Dict:
        if not sentiment:
            return {}

        return {
            "news_sentiment": sentiment.get("news_sentiment"),
            "social_sentiment": sentiment.get("social_sentiment"),
            "earnings_sentiment": sentiment.get("earnings_sentiment"),
        }

    def _summarize_macro(self, macro: Dict) -> Dict:
        if not macro:
            return {}

        return {
            "rates": macro.get("rates"),
            "growth": macro.get("growth"),
            "risk": macro.get("risk"),
        }

    def _summarize_analogs(self, analogs: Dict) -> List[Dict]:
        if not analogs:
            return []

        out = []
        for a in analogs.get("analogs", [])[:3]:
            out.append({
                "ticker": a.get("ticker"),
                "similarity": a.get("similarity"),
                "regime": a.get("regime"),
                "notes": a.get("notes"),
            })
        return out

    # ---------------------------------------------------------
    # LLM call + normalization
    # ---------------------------------------------------------
    def _call_llm(self, prompt: str, state: BrainState) -> str:
        raw = self.llm.run({"text": prompt})

        # LMStudioLLM normalized format
        if isinstance(raw, dict):
            if raw.get("answer"):
                return str(raw["answer"])
            if raw.get("LLM"):
                return str(raw["LLM"])

            # Chat-completion style
            if "choices" in raw and raw["choices"]:
                msg = raw["choices"][0].get("message", {})
                if "content" in msg:
                    return str(msg["content"])

            # Legacy keys
            text = (
                raw.get("text")
                or raw.get("output")
                or raw.get("response")
            )
            if text:
                return str(text)

        return str(raw)

    # ---------------------------------------------------------
    # Main synthesis entry point
    # ---------------------------------------------------------
    def synthesize(self, state: BrainState) -> str:
        meta = getattr(state, "meta", {}) or {}
        sections = meta.get("research_sections")
        ticker = meta.get("ticker", "UNKNOWN")

        if not sections or not self.llm:
            return ""

        # Summaries
        technical_summary = self._summarize_technical(sections.get("technical", {}))
        options_summary = self._summarize_options(sections.get("options", {}))
        sentiment_summary = self._summarize_sentiment(sections.get("sentiment", {}))
        macro_summary = self._summarize_macro(sections.get("macro", {}))
        analogs_summary = self._summarize_analogs(sections.get("analogs", {}))

        # Compact, LLM-friendly prompt
        prompt = f"""
You are Brain-24, a financial research engine.

Write a structured swing-horizon (1–4 weeks) research brief for {ticker}.

User priorities: Technical, Sentiment, Macro, Fundamentals, Catalysts.

[TECHNICAL SUMMARY]
{technical_summary}

[OPTIONS SUMMARY]
{options_summary}

[SENTIMENT SUMMARY]
{sentiment_summary}

[MACRO SUMMARY]
{macro_summary}

[HISTORICAL ANALOGS]
{analogs_summary}

Write sections:
1) Current technical regime
2) Options market & volatility context
3) Sentiment & narrative
4) Macro & sector overlay
5) Historical analogs
6) 1–4 week scenarios (bull/base/bear)
7) Key levels & invalidations
"""

        return self._call_llm(prompt, state)
