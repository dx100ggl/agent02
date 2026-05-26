# brain/c4/tools/builtin/lmstudio_llm.py

import requests
from brain.c4.tools.base import Tool


class LMStudioLLM(Tool):
    """
    C4 tool that sends prompts to LM Studio's local server.

    - Accepts either:
        run("plain prompt")
      or:
        run({"text": "...", "memory_context": "..."})

    - Returns:
        {
            "final": True/False,
            "LLM": "...",
            "thought": "...",
            "answer": "...",
        }
    """

    def __init__(
        self,
        name: str = "lmstudio_llm",
        url: str = "http://192.168.0.80:1234/v1/chat/completions",
        model: str = "local-model",
    ):
        super().__init__(name=name)
        self.url = url
        self.model = model

    def _build_prompt(self, prompt):
        """
        Support both:
        - prompt: str
        - prompt: {"text": "...", "memory_context": "..."}
        """
        if isinstance(prompt, dict):
            user_text = prompt.get("text", "")
            memory_context = prompt.get("memory_context", "") or ""
        else:
            user_text = str(prompt)
            memory_context = ""

        if memory_context.strip():
            full_prompt = f"""
You are an assistant with access to retrieved memory.

User question:
{user_text}

Relevant memory:
{memory_context}

Answer the user naturally, using the memory if it helps.
""".strip()
        else:
            full_prompt = user_text

        return full_prompt

    def run(self, prompt):
        full_prompt = self._build_prompt(prompt)

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": full_prompt}],
            "temperature": 0.7,
        }

        try:
            resp = requests.post(self.url, json=payload, timeout=30)
            data = resp.json()

            # ---------------------------------------------------------
            # 1. Chat-style response
            # ---------------------------------------------------------
            if "choices" in data and data["choices"]:
                choice = data["choices"][0]

                # Chat format
                if "message" in choice and "content" in choice["message"]:
                    answer = choice["message"]["content"]
                    return {
                        "final": True,
                        "LLM": answer,
                        "thought": "LLM response",
                        "answer": answer,
                    }

                # Text completion format
                if "text" in choice:
                    answer = choice["text"]
                    return {
                        "final": True,
                        "LLM": answer,
                        "thought": "LLM response",
                        "answer": answer,
                    }

            # ---------------------------------------------------------
            # 2. LM Studio sometimes returns errors in JSON
            # ---------------------------------------------------------
            if "error" in data:
                return {
                    "error": True,
                    "message": data["error"],
                    "LLM": "",
                    "thought": "LLM error",
                }

            # ---------------------------------------------------------
            # 3. Unexpected format
            # ---------------------------------------------------------
            return {
                "error": True,
                "message": f"Unexpected LM Studio response: {data}",
                "LLM": "",
                "thought": "Unexpected response",
            }

        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "LLM": "",
                "thought": "Exception raised",
            }
