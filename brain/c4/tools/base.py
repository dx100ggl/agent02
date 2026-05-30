# brain/c4/tools/base.py

class Tool:
    name: str
    description: str

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    def run(self, *args, **kwargs):
        raise NotImplementedError("Tool subclasses must implement run()")
