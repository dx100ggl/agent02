# brain/c1/state.py

from __future__ import annotations
import uuid

class BrainState:
    """
    Canonical state object passed through C1 → C2 → C5.
    Compatible with legacy S4 tests expecting:
      - task_id
      - user_id
      - meta
      - history
      - done
    """

    def __init__(self, user_input: str = "", memory=None, context=None):
        self.user_input = user_input or ""
        self.memory = memory
        self.context = context or {}

        # S4 compatibility fields
        self.task_id = str(uuid.uuid4())     # required by orchestrator + tests
        self.user_id = "default_user"        # tests expect this to exist

        # Brain-24 fields
        self.meta = {}
        self.history = []
        self.tool_results = {}
        self.done = False

    def add_history(self, message):
        self.history.append(message)


# Backward compatibility alias
State = BrainState
