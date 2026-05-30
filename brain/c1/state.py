# brain/c1/state.py

from brain.c3.memory.retriever import SimpleMemoryProvider

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
        self.meta = {}          # NEW: required for router + research pipeline
        
        # NEW: required for Executor
        self.memory = SimpleMemoryProvider()    

# --- Backwards compatibility shim ---
# Many legacy modules still import BrainState.
BrainState = State
