# tests/test_s4_memory_and_hooks.py

from __future__ import annotations

from brain.build import build_brain
from brain.c5.integration.c3_hooks import C3MemoryHooks, MemoryHookContext


def test_s4_c3_hooks_write_and_retrieve():
    brain = build_brain(use_lmstudio=False)

    hooks: C3MemoryHooks = brain.c3_hooks
    ctx = MemoryHookContext(task_id="s4_hooks", user_id="user-1", phase="reflection")

    # Write a reflection summary
    summary_id = hooks.on_reflection_summary(
        summary="S4 reflection summary test",
        context=ctx,
        extra_metadata={"tag": "s4_test"},
    )
    assert isinstance(summary_id, str)

    # Retrieve it
    results = hooks.retrieve_for_reflection(
        query="S4 reflection summary test",
        context=ctx,
        top_k=5,
        extra_filter={"tag": "s4_test"},
    )

    assert isinstance(results, list)
    assert any("S4 reflection summary test" in r.record.content for r in results)


def test_s4_memory_stats_available():
    brain = build_brain(use_lmstudio=False)
    hooks: C3MemoryHooks = brain.c3_hooks

    stats = hooks.stats()
    assert isinstance(stats, dict)
