from brain.state import BrainState

class Router:
    def route(self, state: BrainState) -> str:
        raise NotImplementedError
