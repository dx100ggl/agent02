from brain.c1.state import BrainState

class Router:
    def route(self, state: BrainState) -> str:
        raise NotImplementedError
