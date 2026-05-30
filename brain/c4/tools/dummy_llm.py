# brain/c4/tools/dummy_llm.py

class DummyLLMTool:
    """
    A minimal LLM tool that returns a canned response.
    Useful for testing research mode without a real LLM backend.
    """

    def run(self, payload: dict):
        prompt = payload.get("text", "")
        return {
            "text": f"[Dummy LLM] Response to: {prompt}"
        }
