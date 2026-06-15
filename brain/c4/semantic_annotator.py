# brain/c4/semantic_annotator.py

from typing import Dict, Any, List

from brain.llm.lmstudio_llm import LMStudioLLM


class SemanticAnnotator:
    """
    C4 organ: adds lightweight semantic tags to C3 nodes using an LLM.
    Safe: only writes tags into node['metadata']['tags'].
    """

    def __init__(self, llm: LMStudioLLM | None = None):
        # Allow passing an LLM, or create a default one.
        self._llm = llm or LMStudioLLM()

    def annotate_nodes(self, nodes: List[Dict[str, Any]]) -> None:
        """
        In-place annotation of nodes with semantic tags.
        Each node is expected to have at least a 'content' field.
        """
        for node in nodes:
            content = node.get("content", "")
            if not content:
                continue

            prompt = (
                "You are a tagging engine. "
                "Given the following user memory, return 3-5 short, comma-separated tags "
                "that describe its semantics. "
                "Memory: " + repr(content)
            )

            tags_text = self._llm.complete(prompt)
            # Very simple parsing: split on commas, strip whitespace.
            tags = [t.strip() for t in tags_text.split(",") if t.strip()]

            meta = node.setdefault("metadata", {})
            meta["tags"] = tags
