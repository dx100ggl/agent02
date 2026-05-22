from brain.c1.state import BrainState

class Synthesizer:
    def synthesize(self, state: BrainState):
        return state.history[-1]["result"]
