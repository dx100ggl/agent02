# brain/c4/tools/dummy_llm.py

class DummyLLMTool:
    """
    Minimal LLM tool for testing research mode.
    Accepts keyword arguments because Executor calls run(**kwargs).
    """

    def run(self, **kwargs):
        text = kwargs.get("text", "")
        return {"text": f"[Dummy LLM] Response to: {text}"}
