# brain/c4/tools/builtin/yfinance_normalizer.py

from typing import Any, Dict, List
import statistics


class YFinanceOptionsNormalizer:
    """
    Convert yfinance options chain → B2 schema.
    """

    def normalize(self, ticker: str, raw: Dict[str, Any]) -> Dict[str, Any] | None:
        chains = raw.get("chains")
        if not chains:
            return None

        all_contracts: List[Dict[str, float]] = []
        b2_chain = []

        for exp, bucket in chains.items():
            calls = [self._contract(c) for c in bucket.get("calls", [])]
            puts = [self._contract(p) for p in bucket.get("puts", [])]

            all_contracts.extend(calls)
            all_contracts.extend(puts)

            b2_chain.append({
                "expiration": exp,
                "calls": calls,
                "puts": puts,
            })

        if not all_contracts:
            return None

        iv_values = [c["iv"] for c in all_contracts if c["iv"] > 0]
        iv = statistics.mean(iv_values) if iv_values else 0.0

        iv_rank, iv_percentile = self._compute_iv_rank_percentile(iv_values, iv)
        greeks = self._aggregate_greeks(all_contracts)

        return {
            "ticker": ticker,
            "iv": iv,
            "iv_rank": iv_rank,
            "iv_percentile": iv_percentile,
            "greeks": greeks,
            "chain": b2_chain,
        }

    # ---------------- helpers ---------------- #

    def _contract(self, c: Dict[str, Any]) -> Dict[str, float]:
        return {
            "strike": self._safe(c.get("strike")),
            "bid": self._safe(c.get("bid")),
            "ask": self._safe(c.get("ask")),
            "iv": self._safe(c.get("impliedVolatility")),
            "delta": self._safe(c.get("delta")),
            "gamma": self._safe(c.get("gamma")),
            "theta": self._safe(c.get("theta")),
            "vega": self._safe(c.get("vega")),
        }

    @staticmethod
    def _safe(v: Any) -> float:
        try:
            return float(v)
        except Exception:
            return 0.0

    def _aggregate_greeks(self, contracts: List[Dict[str, float]]):
        if not contracts:
            return {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}

        def col(name: str):
            return [c.get(name, 0.0) for c in contracts]

        return {
            "delta": statistics.mean(col("delta")),
            "gamma": statistics.mean(col("gamma")),
            "theta": statistics.mean(col("theta")),
            "vega": statistics.mean(col("vega")),
        }

    def _compute_iv_rank_percentile(self, iv_values, current_iv):
        if not iv_values:
            return 0.0, 0.0

        lo = min(iv_values)
        hi = max(iv_values)

        iv_rank = 0.0 if hi == lo else (current_iv - lo) / (hi - lo)
        iv_percentile = sum(1 for v in iv_values if v <= current_iv) / len(iv_values)

        return iv_rank, iv_percentile
