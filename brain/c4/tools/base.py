class Tool:
    name: str
    description: str
    
    def __init__(self, name: str):
        self.name = name

    def run(self, *args, **kwargs):
        raise NotImplementedError("Tool subclasses must implement run()")