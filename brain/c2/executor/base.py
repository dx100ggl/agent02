from brain.c1.state import BrainState

class ExecutorBase:
    def execute(self, step: dict, state: BrainState):
        raise NotImplementedError
