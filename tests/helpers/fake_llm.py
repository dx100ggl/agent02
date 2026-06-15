# tests/helpers/fake_llm.py

class FakeLLM:
    """
    Minimal LLM stub used in tests.
    Must support:
        - complete(prompt)
        - run(args)
        - __call__(prompt)
    """

    def complete(self, prompt: str) -> str:
        # Always return a deterministic JSON dict for argument repair
        return '{"repaired": true}'

    def run(self, args):
        # Tools expect run({"text": ...})
        text = args.get("text") if isinstance(args, dict) else str(args)
        return {"text": f"FAKE: {text}"}

    def __call__(self, prompt: str) -> str:
        return self.complete(prompt)
