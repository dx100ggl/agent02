# brain/c5/trace_logger.py

from brain.c5.trace_pretty import print_trace

class TraceLogger:
    """
    Lightweight, append-only trace logger for C5 introspection.
    Writes human-readable strings into state.trace_log.
    """

    @staticmethod
    def log(state, message: str):
        if hasattr(state, "trace_log"):
            state.trace_log.append(message)

    @staticmethod
    def log_planner(state, plan):
        TraceLogger.log(state, f"[planner] plan = {plan}")

    @staticmethod
    def log_router(state, mode):
        TraceLogger.log(state, f"[router] mode = {mode}")

    @staticmethod
    def log_executor(state, step, result):
        TraceLogger.log(state, f"[executor] step={step} → result={result}")

    @staticmethod
    def log_reflection(state, reflection_output):
        TraceLogger.log(state, f"[reflection] findings={reflection_output.findings}")
        TraceLogger.log(state, f"[reflection] directives={reflection_output.directives}")
        TraceLogger.log(state, f"[reflection] memory_updates={reflection_output.memory_updates}")

    @staticmethod
    def log_final(state, final_output):
        TraceLogger.log(state, f"[final] output={final_output}")

    @staticmethod
    def dump(state):
        print_trace(state)
