from brain.c4.tools.base import Tool

class EchoTool(Tool):
    name = "echo"
    description = "Echoes input"

    def run(self, text: str):
        return {"echo": text}
