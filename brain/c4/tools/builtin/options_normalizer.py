# brain/c4/tools/builtin/options_normalizer.py

from typing import Any, Dict, List, Tuple
import math
import statistics


class OptionsChainNormalizer:
    """
    Converts Polygon snapshot options chain data into the exact B2 schema.

    B2 schema (must match exactly):
    {
        "ticker": str,
        "iv": float,
        "iv_rank": float,
        "iv_percentile": float,
        "greeks": {
            "delta": float,
            "gamma": float,
            "theta": float,
            "vega": float,
        },
        "chain": [
            {
                "expiration": str,
                "calls": [ {contract} ],
                "puts":  [ {contract} ],
            },
            ...
        ]
    }

    Contract schema:
    {
        "strike": float,
        "bid": float,
        "ask": float,
        "iv": float,
        "delta": float,
        "gamma": float,
        "theta": float,
        "vega": float,
    }
    """

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------

    def normalize(self, ticker: str, raw_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: convert Polygon snapshot → B2 schema.
        """

        # Extract all contracts from Polygon snapshot
        contracts = self._extract_contracts(raw_snapshot)

        if not contracts:
            # If Polygon returns nothing, return an empty-but-valid B2 structure
            return self._empty_b2(ticker)

        # Compute IV metrics
        iv_values = [c["iv"] for c in contracts if c["iv"] is not None]
        iv = statistics.mean(iv_values) if iv_values else 0.0

        iv_rank, iv_percentile = self._compute_iv_rank_percentile(iv_values, iv)

        # Compute aggregate greeks (simple mean)
        greeks = self._compute_aggregate_greeks(contracts)

        # Group by expiration → calls/puts
        chain = self._group_by_expiration(contracts)

        return {
            "ticker": ticker,
            "iv": iv,
            "iv_rank": iv_rank,
            "iv_percentile": iv_percentile,
            "greeks": greeks,
            "chain": chain,
        }

    # ----------------------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------------------

    def _extract_contracts(self, snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Polygon snapshot format:
        {
            "status": "OK",
            "results": {
                "underlying_asset": {...},
                "options": [
                    {
                        "details": {
                            "contract_type": "call" | "put",
                            "expiration_date": "2024-06-21",
                            "strike_price": 100.0,
                        },
                        "last_quote": {
                            "bid": 1.23,
                            "ask": 1.45,
                        },
                        "greeks": {
                            "delta": ...,
                            "gamma": ...,
                            "theta": ...,
                            "vega": ...,
                            "iv": ...,
                        }
                    },
                    ...
                ]
            }
        }
        """

        results = snapshot.get("results", {})
        options = results.get("options", [])
        out = []

        for opt in options:
            details = opt.get("details", {})
            greeks = opt.get("greeks", {})
            quote = opt.get("last_quote", {})

            contract_type = details.get("contract_type")
            if contract_type not in ("call", "put"):
                continue

            expiration = details.get("expiration_date")
            strike = details.get("strike_price")

            bid = quote.get("bid")
            ask = quote.get("ask")

            iv = greeks.get("iv")
            delta = greeks.get("delta")
            gamma = greeks.get("gamma")
            theta = greeks.get("theta")
            vega = greeks.get("vega")

            # Skip malformed entries
            if expiration is None or strike is None:
                continue

            out.append({
                "type": contract_type,
                "expiration": expiration,
                "strike": float(strike),
                "bid": float(bid) if bid is not None else 0.0,
                "ask": float(ask) if ask is not None else 0.0,
                "iv": float(iv) if iv is not None else 0.0,
                "delta": float(delta) if delta is not None else 0.0,
                "gamma": float(gamma) if gamma is not None else 0.0,
                "theta": float(theta) if theta is not None else 0.0,
                "vega": float(vega) if vega is not None else 0.0,
            })

        return out

    # ----------------------------------------------------------------------

    def _compute_iv_rank_percentile(
        self, iv_values: List[float], current_iv: float
    ) -> Tuple[float, float]:
        """
        Session-local IV rank + percentile.
        Rank = (current_iv - min) / (max - min)
        Percentile = fraction of values <= current_iv
        """

        if not iv_values:
            return 0.0, 0.0

        lo = min(iv_values)
        hi = max(iv_values)

        if hi == lo:
            iv_rank = 0.0
        else:
            iv_rank = (current_iv - lo) / (hi - lo)

        # Percentile
        count_le = sum(1 for v in iv_values if v <= current_iv)
        iv_percentile = count_le / len(iv_values)

        return iv_rank, iv_percentile

    # ----------------------------------------------------------------------

    def _compute_aggregate_greeks(self, contracts: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        B2 expects a single greeks dict at top level.
        We compute simple means.
        """

        if not contracts:
            return {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}

        deltas = [c["delta"] for c in contracts]
        gammas = [c["gamma"] for c in contracts]
        thetas = [c["theta"] for c in contracts]
        vegas = [c["vega"] for c in contracts]

        return {
            "delta": statistics.mean(deltas),
            "gamma": statistics.mean(gammas),
            "theta": statistics.mean(thetas),
            "vega": statistics.mean(vegas),
        }

    # ----------------------------------------------------------------------

    def _group_by_expiration(self, contracts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert flat list → B2 chain structure:
        [
            {
                "expiration": "2024-06-21",
                "calls": [ ... ],
                "puts":  [ ... ],
            },
            ...
        ]
        """

        buckets = {}

        for c in contracts:
            exp = c["expiration"]
            if exp not in buckets:
                buckets[exp] = {"calls": [], "puts": []}

            entry = {
                "strike": c["strike"],
                "bid": c["bid"],
                "ask": c["ask"],
                "iv": c["iv"],
                "delta": c["delta"],
                "gamma": c["gamma"],
                "theta": c["theta"],
                "vega": c["vega"],
            }

            if c["type"] == "call":
                buckets[exp]["calls"].append(entry)
            else:
                buckets[exp]["puts"].append(entry)

        # Sort expirations chronologically
        out = []
        for exp in sorted(buckets.keys()):
            # Sort strikes ascending for deterministic output
            calls = sorted(buckets[exp]["calls"], key=lambda x: x["strike"])
            puts = sorted(buckets[exp]["puts"], key=lambda x: x["strike"])

            out.append({
                "expiration": exp,
                "calls": calls,
                "puts": puts,
            })

        return out

    # ----------------------------------------------------------------------

    def _empty_b2(self, ticker: str) -> Dict[str, Any]:
        """
        Return a valid empty B2 structure if Polygon returns nothing.
        """

        return {
            "ticker": ticker,
            "iv": 0.0,
            "iv_rank": 0.0,
            "iv_percentile": 0.0,
            "greeks": {
                "delta": 0.0,
                "gamma": 0.0,
                "theta": 0.0,
                "vega": 0.0,
            },
            "chain": [],
        }
