# tests/test_s4_full_cycle.py

from __future__ import annotations

from brain.build import build_brain
from brain.c1.state import State
from brain.c5.integration.c3_hooks import C3MemoryHooks


def test_s4_full_cycle_reflection_persists_summary():
    """
    Full S4 smoke:
    - build brain
    - run a turn
    - ensure reflection summary is written to C3 via hooks
    """
    brain = build_brain(use_lmstudio=False)

    state = State("Test S4 full cycle with reflection and memory.")
    output = brain.run(state)

    assert isinstance(output, str)
    assert output

    hooks: C3MemoryHooks = brain.c3_hooks

    results = hooks.retrieve_for_reflection(
        query="Findings:",
        context=None,
        top_k=20,
        extra_filter={"type": "reflection_summary"},
    )

    assert isinstance(results, list)
    assert len(results) >= 1
