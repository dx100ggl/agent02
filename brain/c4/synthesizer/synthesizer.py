# brain/c4/synthesizer/synthesizer.py
from __future__ import annotations

from typing import Optional

from brain.c2.executor.executor import ExecutionContext
from brain.c4.tools.builtin.fundamentals_tool import (
    FundamentalsResult,
    FundamentalsSnapshot,
)


class ResearchSynthesizer:
    def __init__(self, llm: Any) -> None:
        self._llm = llm

    # -----------------------------------------------------------------------
    # Main synthesis entrypoint
    # -----------------------------------------------------------------------

    def synthesize_equity_research(
        self,
        ticker: str,
        intent: str,
        exec_ctx: ExecutionContext,
    ) -> str:

        fundamentals: Optional[FundamentalsResult] = exec_ctx.get_result("fundamentals")

        fundamentals_section = (
            self._render_fundamentals_section(fundamentals)
            if fundamentals
            else "No fundamentals snapshot available."
        )

        return f"""Equity Research Note: {ticker}

Intent:
{intent}

Fundamentals Summary:
{fundamentals_section}
""".strip()

    # -----------------------------------------------------------------------
    # Fundamentals Section Renderer
    # -----------------------------------------------------------------------

    def _render_fundamentals_section(
        self,
        result: FundamentalsResult,
    ) -> str:

        s: FundamentalsSnapshot = result.snapshot
        lines: list[str] = []

        lines.append(f"- Ticker: {result.ticker}")
        if result.as_of:
            lines.append(f"- As-of: {result.as_of}")

        lines.append("")
        lines.append("Revenue & Earnings:")
        lines.append(f"  - Revenue (TTM): {s.revenue_ttm or 'n/a'}")
        lines.append(f"  - Revenue YoY growth: {s.revenue_yoy_growth or 'n/a'}")
        lines.append(f"  - EPS diluted (TTM): {s.eps_diluted_ttm or 'n/a'}")
        lines.append(f"  - EPS YoY growth: {s.eps_yoy_growth or 'n/a'}")

        lines.append("")
        lines.append("Margins:")
        lines.append(f"  - Gross margin: {s.gross_margin or 'n/a'}")
        lines.append(f"  - Operating margin: {s.operating_margin or 'n/a'}")
        lines.append(f"  - Net margin: {s.net_margin or 'n/a'}")

        lines.append("")
        lines.append("Growth:")
        lines.append(f"  - Revenue CAGR (3y): {s.revenue_cagr_3y or 'n/a'}")
        lines.append(f"  - EPS CAGR (3y): {s.eps_cagr_3y or 'n/a'}")

        lines.append("")
        lines.append("Valuation:")
        lines.append(f"  - P/E (TTM): {s.pe_ttm or 'n/a'}")
        lines.append(f"  - Forward P/E: {s.forward_pe or 'n/a'}")
        lines.append(f"  - EV/EBITDA: {s.ev_ebitda or 'n/a'}")
        lines.append(f"  - Price/Sales: {s.price_sales or 'n/a'}")

        lines.append("")
        lines.append("Guidance & Outlook:")
        lines.append(f"  - Management guidance: {s.management_guidance_summary or 'n/a'}")
        lines.append(f"  - Key guidance metrics: {s.key_guidance_metrics or 'n/a'}")

        lines.append("")
        lines.append("Qualitative Notes:")
        lines.append(f"  - Business quality: {s.business_quality_notes or 'n/a'}")
        lines.append(f"  - Risk factors: {s.risk_factors_notes or 'n/a'}")
        lines.append(f"  - Accounting quality: {s.accounting_quality_notes or 'n/a'}")

        return "\n".join(lines)
