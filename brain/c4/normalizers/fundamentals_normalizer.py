# brain/c4/normalizers/fundamentals_normalizer.py

from __future__ import annotations
from typing import Any, Dict
from .normalizer_base import Normalizer


class FundamentalsNormalizer(Normalizer):
    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            return {}

        snap = raw.get("snapshot", {})

        return {
            "growth": {
                "revenue_yoy": snap.get("revenue_yoy_growth"),
                "eps_yoy": snap.get("eps_yoy_growth"),
                "revenue_cagr_3y": snap.get("revenue_cagr_3y"),
                "eps_cagr_3y": snap.get("eps_cagr_3y"),
            },
            "margins": {
                "gross": snap.get("gross_margin"),
                "operating": snap.get("operating_margin"),
                "net": snap.get("net_margin"),
            },
            "valuation": {
                "pe_ttm": snap.get("pe_ttm"),
                "forward_pe": snap.get("forward_pe"),
                "ev_ebitda": snap.get("ev_ebitda"),
                "price_sales": snap.get("price_sales"),
            },
            "guidance": {
                "summary": snap.get("management_guidance_summary"),
                "metrics": snap.get("key_guidance_metrics"),
            },
            "qualitative": {
                "business_quality": snap.get("business_quality_notes"),
                "risk_factors": snap.get("risk_factors_notes"),
                "accounting_quality": snap.get("accounting_quality_notes"),
            },
        }
