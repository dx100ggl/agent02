from typing import Any, Dict, List, Optional
from brain.c1.state import BrainState


class Synthesizer:
    def __init__(self, llm=None):
        self.llm = llm

    # ---------------------------------------------------------
    # Internal: call LLM and normalize all formats
    # ---------------------------------------------------------
    def _call_llm(self, prompt: str, state: BrainState) -> str:
        if not self.llm:
            return ""

        payload: Dict[str, Any] = {"text": prompt}

        # Optional: memory context
        if getattr(state, "memory_results", None):
            lines = []
            for item in state.memory_results:
                content = item.get("content", "")
                if content:
                    lines.append(f"- {content}")
            if lines:
                payload["memory_context"] = "\n".join(lines)

        raw = self.llm.run(payload)

        print("\n\n=== DEBUG: RAW LLM OUTPUT ===")
        print(raw)
        print("=== END DEBUG ===\n\n")

        # Unwrap executor-wrapped tool output
        if isinstance(raw, dict) and "result" in raw and isinstance(raw["result"], dict):
            raw = raw["result"]

        # LM Studio / OpenAI-style chat completion
        if isinstance(raw, dict):
            if raw.get("answer"):
                return str(raw["answer"])
            if raw.get("LLM"):
                return str(raw["LLM"])

            if "choices" in raw and raw["choices"]:
                choice = raw["choices"][0]
                msg = choice.get("message", {})
                if "content" in msg:
                    return str(msg["content"])
                if "text" in choice:
                    return str(choice["text"])

            text = (
                raw.get("text")
                or raw.get("output")
                or raw.get("response")
            )
            if text:
                return str(text)

        return str(raw)

    # ---------------------------------------------------------
    # Helpers: build compact summaries from raw sections
    # ---------------------------------------------------------
    def _build_technical_summary(self, technical: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not isinstance(technical, dict):
            return {}

        ohlcv: List[Dict[str, Any]] = technical.get("ohlcv") or []
        if not ohlcv:
            return {"ticker": technical.get("ticker", "UNKNOWN")}

        closes = [row.get("Close") for row in ohlcv if row.get("Close") is not None]
        highs = [row.get("High") for row in ohlcv if row.get("High") is not None]
        lows = [row.get("Low") for row in ohlcv if row.get("Low") is not None]

        last = ohlcv[-1]
        last_close = last.get("Close")

        recent_high = max(highs) if highs else None
        recent_low = min(lows) if lows else None

        trend = "uptrend"
        if len(closes) >= 2 and closes[-1] < closes[-2]:
            trend = "downtrend"

        return {
            "ticker": technical.get("ticker", "UNKNOWN"),
            "trend": trend,
            "recent_high": recent_high,
            "recent_low": recent_low,
            "last_close": last_close,
        }

    def _build_options_summary(self, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not isinstance(options, dict):
            return {}

        greeks = options.get("greeks") or {}
        return {
            "iv": options.get("iv"),
            "iv_rank": options.get("iv_rank"),
            "iv_percentile": options.get("iv_percentile"),
            "delta": greeks.get("delta"),
            "gamma": greeks.get("gamma"),
            "theta": greeks.get("theta"),
            "vega": greeks.get("vega"),
        }

    def _build_sentiment_summary(self, sentiment: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not isinstance(sentiment, dict):
            return {}

        return {
            "news_sentiment": sentiment.get("news_sentiment"),
            "social_sentiment": sentiment.get("social_sentiment"),
            "earnings_sentiment": sentiment.get("earnings_sentiment"),
        }

    def _build_macro_summary(self, macro: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not isinstance(macro, dict):
            return {}

        return {
            "rates": macro.get("rates"),
            "growth": macro.get("growth"),
            "risk": macro.get("risk"),
        }

    def _build_analogs_summary(self, analogs: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not isinstance(analogs, dict):
            return []

        raw = analogs.get("analogs") or []
        out: List[Dict[str, Any]] = []
        for a in raw:
            if not isinstance(a, dict):
                continue
            out.append(
                {
                    "ticker": a.get("ticker"),
                    "similarity": a.get("similarity"),
                    "regime": a.get("regime"),
                    "notes": a.get("notes"),
                }
            )
        return out

    # ---------------------------------------------------------
    # Public: main synthesis entry point
    # ---------------------------------------------------------
    def synthesize(self, state: BrainState) -> str:
        meta = getattr(state, "meta", {}) or {}
        sections = meta.get("research_sections")
        ticker = meta.get("ticker", "UNKNOWN")

        # 1. Research synthesis
        if sections and self.llm:
            technical_raw = sections.get("technical")
            options_raw = sections.get("options")
            sentiment_raw = sections.get("sentiment")
            macro_raw = sections.get("macro")
            analogs_raw = sections.get("analogs")

            technical_summary = self._build_technical_summary(technical_raw)
            options_summary = self._build_options_summary(options_raw)
            sentiment_summary = self._build_sentiment_summary(sentiment_raw)
            macro_summary = self._build_macro_summary(macro_raw)
            analogs_summary = self._build_analogs_summary(analogs_raw)

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
            print("\n=== DEBUG: PROMPT SENT TO LM STUDIO ===")
            print(
                {
                    "model": "local-model",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                }
            )
            print("=== END PROMPT DEBUG ===\n")
            return self._call_llm(prompt, state)

        # 2. Fallback: last tool result
        history = getattr(state, "history", None)
        if history:
            last = history[-1]
            if "result" in last and last["result"]:
                return str(last["result"])
            if "final_output" in last and last["final_output"]:
                return str(last["final_output"])

        return ""
