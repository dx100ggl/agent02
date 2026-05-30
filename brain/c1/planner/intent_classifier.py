# brain/c1/planner/intent_classifier.py

from typing import Protocol

class LLMCallable(Protocol):
    def __call__(self, prompt: str) -> str: ...


class IntentClassifier:
    """
    Classifies user intent into:
      - write_memory
      - retrieve_memory
      - equity_research
      - normal_llm
    """

    def classify(self, llm: LLMCallable, user_input: str) -> str:
        text = user_input.lower()

        # Simple heuristic for research intent
        if "research" in text or "brief" in text or "analysis" in text:
            return "equity_research"

        prompt = f"""
You are an intent classifier for a memory-enabled agent.

Classify the user's intent into exactly one of:
- write_memory
- retrieve_memory
- normal_llm

User input: "{user_input}"

Rules:
- If the user is telling the agent to store a fact for later, classify as write_memory.
- If the user is asking about something they previously told the agent, classify as retrieve_memory.
- Otherwise classify as normal_llm.

Respond with ONLY the label, no explanation.
"""

        raw = llm(prompt)
        label = (raw or "").strip().lower()

        if label in ("write_memory", "retrieve_memory", "normal_llm"):
            return label

        return "normal_llm"
