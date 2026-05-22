from brain.c5.heuristics.planning_rules import detect_missing_preconditions
from brain.c5.heuristics.tool_rules import detect_tool_misuse
from brain.c5.heuristics.hallucination_rules import detect_hallucination
from brain.c5.heuristics.efficiency_rules import detect_redundancy


def test_planning_missing_preconditions():
    trace = [
        {
            "action": "tool_call",
            "tool": "search",
            "preconditions": ["memory_retrieved"],
            "preconditions_satisfied": False,
        }
    ]

    assert detect_missing_preconditions(trace) is True


def test_tool_misuse_detects_missing_argument():
    trace = [
        {
            "tool": "search",
            "args": {"query": None},
            "error": "Missing required argument: query",
        }
    ]

    assert "Missing required argument" in detect_tool_misuse(trace)


def test_hallucination_detects_unexecuted_tool_reference():
    final_output = {"source_tool": "search"}
    planner_trace = []
    executor_trace = []  # no tools executed

    result = detect_hallucination(final_output, planner_trace, executor_trace)
    assert "never executed" in result


def test_efficiency_detects_redundant_calls():
    trace = [
        {"action": "tool_call", "tool": "search", "args": {"q": "x"}},
        {"action": "tool_call", "tool": "search", "args": {"q": "x"}},
    ]

    assert detect_redundancy(trace) is True
