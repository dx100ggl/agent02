# brain/c5/heuristics/hullucination_rules.py

"""
Hallucination detection heuristics for C5 Reflection Engine v1.
Detects mismatches between output and execution trace.
"""

def detect_hallucination(final_output, planner_trace, executor_trace):
    """
    Detects when the final output references:
    - tools that were never called
    - data that was never retrieved
    - results that contradict the trace

    Returns:
        Optional[str]
    """

    # Collect all tool names actually used
    used_tools = {step.get("tool") for step in executor_trace if step.get("tool")}

    # Simple heuristic: if output claims a tool result that never occurred
    if isinstance(final_output, dict):
        claimed_tool = final_output.get("source_tool")
        if claimed_tool and claimed_tool not in used_tools:
            return f"Output references tool '{claimed_tool}' which was never executed."

    # Detect invented fields
    if isinstance(final_output, dict):
        for key, value in final_output.items():
            if value == "__hallucinated__":
                return f"Output contains hallucinated placeholder for field '{key}'."

    # Detect contradiction: executor error but output claims success
    any_errors = any(step.get("error") for step in executor_trace)
    if any_errors and final_output and final_output != {}:
        return "Output claims success despite executor errors."

    return None
