# brain/c5/trace_pretty.py

import sys
from typing import Iterable


# Simple ANSI colors (disabled if stream is not a TTY)
COLORS = {
    "planner": "\033[95m",     # magenta
    "router": "\033[94m",      # blue
    "executor": "\033[92m",    # green
    "reflection": "\033[93m",  # yellow
    "final": "\033[91m",       # red
    "reset": "\033[0m",
}


def _detect_tag(line: str) -> str:
    if line.startswith("[planner]"):
        return "planner"
    if line.startswith("[router]"):
        return "router"
    if line.startswith("[executor]"):
        return "executor"
    if line.startswith("[reflection]"):
        return "reflection"
    if line.startswith("[final]"):
        return "final"
    return ""


def _indent_for_tag(tag: str) -> str:
    if tag in ("planner", "router"):
        return ""
    if tag == "executor":
        return "  "
    if tag == "reflection":
        return "    "
    if tag == "final":
        return ""
    return ""


def _colorize(tag: str, text: str, enable_color: bool) -> str:
    if not enable_color or tag not in COLORS:
        return text
    return f"{COLORS[tag]}{text}{COLORS['reset']}"


def format_trace_lines(lines: Iterable[str], enable_color: bool = True) -> Iterable[str]:
    """
    Turn raw trace_log lines into pretty, indented, optionally colored lines.
    """
    for line in lines:
        tag = _detect_tag(line)
        indent = _indent_for_tag(tag)
        pretty = indent + line
        yield _colorize(tag, pretty, enable_color)


def print_trace(state, stream=None, color: bool = True):
    """
    Pretty-print the trace for a given State.

    Usage:
        result = brain.run(state)
        from brain.c5.trace_pretty import print_trace
        print_trace(state)
    """
    if stream is None:
        stream = sys.stdout

    lines = getattr(state, "trace_log", [])
    enable_color = color and getattr(stream, "isatty", lambda: False)()

    for pretty_line in format_trace_lines(lines, enable_color=enable_color):
        stream.write(pretty_line + "\n")
