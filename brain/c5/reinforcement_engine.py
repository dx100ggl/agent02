# brain/c5/reinforcement_engine.py

from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime, timezone


class C5ReinforcementEngine:
    """
    Reinforces, weakens, or retires beliefs based on:
      - reflection findings
      - execution success/failure
      - cluster persistence
      - contradictions
    """

    def __init__(self, belief_store):
        self.belief_store = belief_store

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------
    def reinforce(
        self,
        reflection_output: Dict[str, Any],
        execution_output: Dict[str, Any],
        clusters: List[Any],
    ):
        """
        Main reinforcement entrypoint.
        """
        beliefs = self.belief_store.all()
        cluster_ids = {c.id for c in clusters}

        for belief in beliefs:
            self._reinforce_single_belief(
                belief,
                reflection_output,
                execution_output,
                cluster_ids,
            )

        # Remove beliefs that have decayed too far
        self._retire_weak_beliefs()

    # ---------------------------------------------------------
    # Internal logic
    # ---------------------------------------------------------
    def _reinforce_single_belief(
        self,
        belief,
        reflection_output,
        execution_output,
        cluster_ids,
    ):
        now = datetime.now(timezone.utc).isoformat()

        # 1. Cluster persistence → strengthen
        if belief.cluster_id in cluster_ids:
            belief.strength = min(1.0, belief.strength + 0.05)
            belief.updated_at = now

        # 2. Execution success → strengthen
        final = execution_output.get("final", {})
        if isinstance(final, dict) and not final.get("error"):
            belief.strength = min(1.0, belief.strength + 0.05)

        # 3. Reflection contradictions → weaken
        contradictions = [
            f for f in reflection_output.get("findings", [])
            if "contradiction" in f.get("label", "").lower()
        ]
        if contradictions:
            belief.strength = max(0.0, belief.strength - 0.1)

        # 4. Reflection confirmations → strengthen
        confirmations = [
            f for f in reflection_output.get("findings", [])
            if "consistent" in f.get("label", "").lower()
        ]
        if confirmations:
            belief.strength = min(1.0, belief.strength + 0.05)

        # Save updated belief
        self.belief_store.update(belief)

    def _retire_weak_beliefs(self):
        """
        Remove beliefs that have decayed too far.
        """
        to_remove = [
            b for b in self.belief_store.all()
            if b.strength < 0.05
        ]
        for b in to_remove:
            del self.belief_store._beliefs[b.id]
