# brain/state.py

class State:
    def __init__(self, user_input: str = None):
        self.task_id = None
        self.user_input = user_input
        self.memory_context = []
        self.plan = []
        self.history = []
        self.tool_results = {}
        self.done = False
        self.trace_log = []   # <-- NEW
        self.meta = {}          # for E2-P3

# --- Backwards compatibility shim ---
# Many legacy modules still import BrainState.
BrainState = State
