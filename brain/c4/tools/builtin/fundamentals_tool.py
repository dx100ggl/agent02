# brain/c4/tools/builtin/fundamentals_tool.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

FUNDAMENTALS_TOOL_NAME = "fundamentals"


# ---------------------------------------------------------------------------
# LLM Protocol (matches your dummy_llm + lmstudio_llm interface)
# ---------------------------------------------------------------------------

class LLMClient(Protocol):
    def complete(self, prompt: str, temperature: float = 0.0) -> str:
        ...


# ---------------------------------------------------------------------------
# Request / Result Types
# ---------------------------------------------------------------------------

@dataclass
class FundamentalsRequest:
    ticker: str
    as_of: Optional[str] = None
    region: Optional[str] = None
    sector_hint: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class FundamentalsSnapshot:
    revenue_ttm: Optional[str] = None
    revenue_yoy_growth: Optional[str] = None
    eps_diluted_ttm: Optional[str] = None
    eps_yoy_growth: Optional[str] = None

    gross_margin: Optional[str] = None
    operating_margin: Optional[str] = None
    net_margin: Optional[str] = None

    revenue_cagr_3y: Optional[str] = None
    eps_cagr_3y: Optional[str] = None

    pe_ttm: Optional[str] = None
    forward_pe: Optional[str] = None
    ev_ebitda: Optional[str] = None
    price_sales: Optional[str] = None

    management_guidance_summary: Optional[str] = None
    key_guidance_metrics: Optional[str] = None

    business_quality_notes: Optional[str] = None
    risk_factors_notes: Optional[str] = None
    accounting_quality_notes: Optional[str] = None


@dataclass
class FundamentalsResult:
    ticker: str
    as_of: Optional[str]
    snapshot: FundamentalsSnapshot
    raw_model_text: str


# ---------------------------------------------------------------------------
# Tool Implementation
# ---------------------------------------------------------------------------

class FundamentalsTool:
    """
    C4 Fundamentals Tool (builtin).

    Mirrors the structure of your existing builtin tools:
    - market_data_tool.py
    - options_data_tool.py
    - technicals_tool.py
    """

    name: str = FUNDAMENTALS_TOOL_NAME

    # -----------------------------------------------------------------------
    # Public entrypoint used by C2 executor
    # -----------------------------------------------------------------------
    def run(
        self,
        llm: LLMClient,
        request: FundamentalsRequest,
        ctx: Optional[Dict[str, Any]] = None,
    ) -> FundamentalsResult:

        prompt = self._build_prompt(request)
        raw_text = llm.complete(prompt=prompt, temperature=0.1)

        import re
        import json

        # Clean markdown fences
        clean_text = raw_text.strip()
        clean_text = re.sub(r"^```(?:json)?", "", clean_text, flags=re.IGNORECASE).strip()
        clean_text = re.sub(r"```$", "", clean_text).strip()

        try:
            parsed = json.loads(clean_text)
        except Exception:
            parsed = {
                "ticker": request.ticker,
                "as_of": request.as_of,
                "snapshot": {
                    "management_guidance_summary": raw_text[:2000],
                },
            }

        return self._parse_result(request, raw_text, parsed)

    # -----------------------------------------------------------------------
    # Prompt builder
    # -----------------------------------------------------------------------
    def _build_prompt(self, request: FundamentalsRequest) -> str:
        ticker = request.ticker.upper()
        as_of = request.as_of or "latest available"
        region = request.region or "global"
        sector_hint = request.sector_hint or "N/A"
        notes = request.notes or "N/A"

        return f"""
You are a disciplined equity research analyst.

Task:
Provide a compact fundamentals snapshot for the company with ticker "{ticker}".
Focus on summarized metrics only. Do NOT return raw financial statements,
tables of line items, or full income/balance/cash flow statements.

Context:
- Ticker: {ticker}
- As-of date: {as_of}
- Region: {region}
- Sector hint: {sector_hint}
- Additional notes: {notes}

Requirements:
1. Only provide summarized fields. No raw financial statements.
2. Use short, human-readable values (e.g., "USD 12.3B", "18.4%", "mid-teens").
3. If a field is not reasonably inferable, set it to null.
4. Keep commentary concise and analytical.

Return JSON with this exact shape:

{{
  "ticker": "<string>",
  "as_of": "<string or null>",
  "snapshot": {{
    "revenue_ttm": "<string or null>",
    "revenue_yoy_growth": "<string or null>",
    "eps_diluted_ttm": "<string or null>",
    "eps_yoy_growth": "<string or null>",

    "gross_margin": "<string or null>",
    "operating_margin": "<string or null>",
    "net_margin": "<string or null>",

    "revenue_cagr_3y": "<string or null>",
    "eps_cagr_3y": "<string or null>",

    "pe_ttm": "<string or null>",
    "forward_pe": "<string or null>",
    "ev_ebitda": "<string or null>",
    "price_sales": "<string or null>",

    "management_guidance_summary": "<string or null>",
    "key_guidance_metrics": "<string or null>",

    "business_quality_notes": "<string or null>",
    "risk_factors_notes": "<string or null>",
    "accounting_quality_notes": "<string or null>"
  }}
}}
""".strip()

    # -----------------------------------------------------------------------
    # Parse LLM JSON → Result object
    # -----------------------------------------------------------------------
    def _parse_result(
        self,
        request: FundamentalsRequest,
        raw_text: str,
        parsed: Dict[str, Any],
    ) -> FundamentalsResult:

        snap = parsed.get("snapshot") or {}

        snapshot = FundamentalsSnapshot(
            revenue_ttm=snap.get("revenue_ttm"),
            revenue_yoy_growth=snap.get("revenue_yoy_growth"),
            eps_diluted_ttm=snap.get("eps_diluted_ttm"),
            eps_yoy_growth=snap.get("eps_yoy_growth"),

            gross_margin=snap.get("gross_margin"),
            operating_margin=snap.get("operating_margin"),
            net_margin=snap.get("net_margin"),

            revenue_cagr_3y=snap.get("revenue_cagr_3y"),
            eps_cagr_3y=snap.get("eps_cagr_3y"),

            pe_ttm=snap.get("pe_ttm"),
            forward_pe=snap.get("forward_pe"),
            ev_ebitda=snap.get("ev_ebitda"),
            price_sales=snap.get("price_sales"),

            management_guidance_summary=snap.get("management_guidance_summary"),
            key_guidance_metrics=snap.get("key_guidance_metrics"),

            business_quality_notes=snap.get("business_quality_notes"),
            risk_factors_notes=snap.get("risk_factors_notes"),
            accounting_quality_notes=snap.get("accounting_quality_notes"),
        )

        return FundamentalsResult(
            ticker=parsed.get("ticker") or request.ticker,
            as_of=parsed.get("as_of") or request.as_of,
            snapshot=snapshot,
            raw_model_text=raw_text,
        )


# ---------------------------------------------------------------------------
# Registry Integration
# ---------------------------------------------------------------------------

def register_fundamentals_tool(registry: Any) -> None:
    """
    Register the FundamentalsTool using the canonical naming pattern
    used by all other builtin tools.
    """
    registry.register("fundamentals", FundamentalsTool())