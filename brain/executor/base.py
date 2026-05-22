from brain.state import BrainState

class ExecutorBase:
    def execute(self, step: dict, state: BrainState):
        raise NotImplementedError
