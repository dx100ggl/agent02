# brain/c4/tools/builtin/eodhd_normalizer.py

from typing import Any, Dict, List
import statistics


class EODHDOptionsNormalizer:
    """
    Convert EODHD options chain → B2-compatible schema.

    Expected EODHD shape (simplified):

    {
      "code": "success",
      "data": [
        {
          "expirationDate": "2024-06-21",
          "type": "call" | "put",
          "strike": 100.0,
          "bid": 1.23,
          "ask": 1.45,
          "impliedVolatility": 0.42,
          "delta": 0.5,
          "gamma": 0.01,
          "theta": -0.02,
          "vega": 0.1,
          ...
        },
        ...
      ]
    }
    """

    def normalize(self, ticker: str, raw: Dict[str, Any]) -> Dict[str, Any] | None:
        data = raw.get("data")
        if not isinstance(data, list) or not data:
            return None

        # Group contracts by expiration
        expiries: Dict[str, Dict[str, List[Dict[str, float]]]] = {}
        all_contracts: List[Dict[str, float]] = []

        for opt in data:
            exp = opt.get("expirationDate")
            if not exp:
                continue

            exp_bucket = expiries.setdefault(exp, {"calls": [], "puts": []})

            contract = {
                "strike": self._safe_num(opt.get("strike")),
                "bid": self._safe_num(opt.get("bid")),
                "ask": self._safe_num(opt.get("ask")),
                "iv": self._safe_num(opt.get("impliedVolatility")),
                "delta": self._safe_num(opt.get("delta")),
                "gamma": self._safe_num(opt.get("gamma")),
                "theta": self._safe_num(opt.get("theta")),
                "vega": self._safe_num(opt.get("vega")),
            }

            all_contracts.append(contract)

            if opt.get("type") == "call":
                exp_bucket["calls"].append(contract)
            else:
                exp_bucket["puts"].append(contract)

        if not all_contracts:
            return None

        # IV metrics
        iv_values = [c["iv"] for c in all_contracts if isinstance(c["iv"], (int, float, float))]
        iv = statistics.mean(iv_values) if iv_values else 0.0
        iv_rank, iv_percentile = self._compute_iv_rank_percentile(iv_values, iv)

        # Aggregate greeks
        greeks = self._aggregate_greeks(all_contracts)

        # Build B2-style chain
        chain = []
        for exp, buckets in sorted(expiries.items()):
            chain.append(
                {
                    "expiration": exp,
                    "calls": buckets["calls"],
                    "puts": buckets["puts"],
                }
            )

        return {
            "ticker": ticker,
            "iv": iv,
            "iv_rank": iv_rank,
            "iv_percentile": iv_percentile,
            "greeks": greeks,
            "chain": chain,
        }

    # ---------------- internal helpers ---------------- #

    @staticmethod
    def _safe_num(v: Any) -> float:
        if isinstance(v, (int, float)):
            return float(v)
        try:
            return float(v)
        except Exception:
            return 0.0

    def _aggregate_greeks(self, contracts: List[Dict[str, float]]) -> Dict[str, float]:
        if not contracts:
            return {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}

        def col(name: str) -> List[float]:
            return [c.get(name, 0.0) for c in contracts]

        return {
            "delta": statistics.mean(col("delta")),
            "gamma": statistics.mean(col("gamma")),
            "theta": statistics.mean(col("theta")),
            "vega": statistics.mean(col("vega")),
        }

    def _compute_iv_rank_percentile(self, iv_values: List[float], current_iv: float):
        if not iv_values:
            return 0.0, 0.0

        lo = min(iv_values)
        hi = max(iv_values)

        iv_rank = 0.0 if hi == lo else (current_iv - lo) / (hi - lo)
        iv_percentile = sum(1 for v in iv_values if v <= current_iv) / len(iv_values)

        return iv_rank, iv_percentile
