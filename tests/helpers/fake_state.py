# tests/helpers/fake_state.py

class FakeState:
    """
    Minimal BrainState stub for tests.
    """

    def __init__(self, user_input: str, memory):
        self.user_input = user_input
        self.memory = memory
        self.meta = {}
        self.history = []
        self.memory_results = None
