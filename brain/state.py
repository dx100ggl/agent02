# brain/state.py

class BrainState:
    def __init__(self, user_input: str):
        self.user_input = user_input
        self.memory_context = []
        self.plan = []
        self.history = []
        self.tool_results = {}
        self.done = False
