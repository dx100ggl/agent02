# brain/c1/planner/base.py

from brain.c1.state import BrainState

class Planner:
    def plan(self, state: BrainState):
        raise NotImplementedError
