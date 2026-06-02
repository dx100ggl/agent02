# tests/helpers/fake_llm.py

class FakeLLM:
    """
    Deterministic fake LLM for tests.
    """

    def __call__(self, prompt: str) -> str:
        # Used by IntentClassifier
        if "write_memory" in prompt:
            return "normal_llm"
        return "normal_llm"

    def run(self, payload):
        # Used by Synthesizer
        text = payload.get("text", "")
        return {
            "text": f"[FAKE LLM OUTPUT]\n{text}\n[END]"
        }
