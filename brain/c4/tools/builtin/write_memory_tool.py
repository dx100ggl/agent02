# brain/c4/tools/builtin/write_memory_tool.py


from brain.c4.tools.base import Tool


class WriteMemoryTool(Tool):
    """
    Tool to write a fact into long-term memory.
    """

    def __init__(self, memory, name: str = "write_memory"):
        super().__init__(name)
        self.memory = memory

    def run(self, fact: str):
        """
        fact: arbitrary text to store as a memory.
        """
        self.memory.write_fact(fact)
        return {
            "final": True,
            "written": fact,
        }
