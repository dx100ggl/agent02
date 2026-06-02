from typing import Any, Dict, List
import statistics

class YahooOptionsNormalizer:
    """
    Convert Yahoo Finance options chain → B2 schema.
    """

    def normalize(self, ticker: str, raw: Dict[str, Any]) -> Dict[str, Any]:
        result = raw.get("optionChain", {}).get("result", [])
        if not result:
            return None

        chain_data = result[0]
        expirations = chain_data.get("expirationDates", [])
        options = chain_data.get("options", [])

        if not options:
            return None

        # Yahoo returns only one expiration per request
        opt = options[0]
        calls = opt.get("calls", [])
        puts = opt.get("puts", [])

        # Extract IV values for rank/percentile
        iv_values = [c.get("impliedVolatility") for c in calls + puts if c.get("impliedVolatility")]
        iv = statistics.mean(iv_values) if iv_values else 0.0

        iv_rank, iv_percentile = self._compute_iv_rank_percentile(iv_values, iv)

        # Aggregate greeks
        greeks = self._aggregate_greeks(calls + puts)

        # Build B2 chain
        chain = [{
            "expiration": str(expirations[0]),
            "calls": [self._contract(c) for c in calls],
            "puts": [self._contract(p) for p in puts],
        }]

        return {
            "ticker": ticker,
            "iv": iv,
            "iv_rank": iv_rank,
            "iv_percentile": iv_percentile,
            "greeks": greeks,
            "chain": chain,
        }

    def _contract(self, c: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "strike": c.get("strike", 0.0),
            "bid": c.get("bid", 0.0),
            "ask": c.get("ask", 0.0),
            "iv": c.get("impliedVolatility", 0.0),
            "delta": c.get("delta", 0.0),
            "gamma": c.get("gamma", 0.0),
            "theta": c.get("theta", 0.0),
            "vega": c.get("vega", 0.0),
        }

    def _aggregate_greeks(self, contracts: List[Dict[str, Any]]):
        if not contracts:
            return {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}

        deltas = [c.get("delta", 0.0) for c in contracts]
        gammas = [c.get("gamma", 0.0) for c in contracts]
        thetas = [c.get("theta", 0.0) for c in contracts]
        vegas = [c.get("vega", 0.0) for c in contracts]

        return {
            "delta": statistics.mean(deltas),
            "gamma": statistics.mean(gammas),
            "theta": statistics.mean(thetas),
            "vega": statistics.mean(vegas),
        }

    def _compute_iv_rank_percentile(self, iv_values, current_iv):
        if not iv_values:
            return 0.0, 0.0

        lo = min(iv_values)
        hi = max(iv_values)

        iv_rank = 0.0 if hi == lo else (current_iv - lo) / (hi - lo)
        iv_percentile = sum(1 for v in iv_values if v <= current_iv) / len(iv_values)

        return iv_rank, iv_percentile
