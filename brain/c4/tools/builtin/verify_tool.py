# brain/c4/tools/builtin/verify_tool.py

from brain.c4.tools.base import Tool


class VerifyTool(Tool):
    """
    No-op verification tool used by cautious mode.
    """

    name = "verify_tool"

    def __init__(self):
        super().__init__(self.name)

    def run(self, args):
        # Always returns a simple verification result
        return {"verified": True}
