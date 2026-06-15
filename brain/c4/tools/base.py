# brain/c4/tools/base.py

class Tool:
    """
    Base class for all C4 tools.
    Updated to support both legacy *args/**kwargs and the new args-dict style.
    """

    name: str
    description: str
    schema: dict = None  # Optional schema for argument validation

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    def run(self, *args, **kwargs):
        """
        Default behavior:
        - If a subclass overrides run(args_dict), we pass kwargs as a dict.
        - If a subclass expects legacy signature, kwargs still works.
        """
        raise NotImplementedError("Tool subclasses must implement run()")

    def normalize_args(self, *args, **kwargs):
        """
        Normalize arguments into a single dict for executor validation.
        Supports:
            run({"query": "hello"})
            run(query="hello")
            run("hello")  # legacy fallback
        """
        # Case 1: run(args_dict)
        if len(args) == 1 and isinstance(args[0], dict):
            return args[0]

        # Case 2: run(query="hello")
        if kwargs:
            return kwargs

        # Case 3: run("hello") → treat as {"input": "..."}
        if len(args) == 1:
            return {"input": args[0]}

        return {}
