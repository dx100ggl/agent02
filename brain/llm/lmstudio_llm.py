# brain/llm/lmstudio_llm.py

from __future__ import annotations

import requests
from typing import Any, Dict, Union
import json

from brain.c4.tools.base import Tool


class LMStudioLLM(Tool):
    """
    S4‑compatible LM Studio LLM tool.

    - Accepts:
        run("plain prompt")
        run({"text": "...", "memory_context": "..."})

    - Returns:
        {
            "final": True,
            "LLM": "...",
            "thought": "LLM response",
            "answer": "...",
        }

    - Fully compatible with:
        • Executor._execute_llm
        • Planner.llm_callable
        • ToolRegistry
        • C3 memory‑aware prompting
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

    # ---------------------------------------------------------
    # Prompt construction (supports memory context)
    # ---------------------------------------------------------
    def _build_prompt(self, payload: Union[str, Dict[str, Any]]) -> str:
        if isinstance(payload, dict):
            user_text = payload.get("text", "")
            memory_context = payload.get("memory_context", "") or ""
        else:
            user_text = str(payload)
            memory_context = ""

        if memory_context.strip():
            return (
                "You are an assistant with access to retrieved memory.\n\n"
                "User question:\n"
                f"{user_text}\n\n"
                "Relevant memory:\n"
                f"{memory_context}\n\n"
                "Answer the user naturally, using the memory if it helps."
            )

        return user_text

    # ---------------------------------------------------------
    # Main run() entry point
    # ---------------------------------------------------------
    def run(self, payload: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Core LM Studio call.
        Returns a dict with keys: final, LLM, thought, answer.
        """
        full_prompt = self._build_prompt(payload)

        request_body = {
            "model": self.model,
            "messages": [{"role": "user", "content": full_prompt}],
            "temperature": 0.7,
        }
        print("\n\n=== DEBUG: PROMPT SENT TO LM STUDIO ===")
        print(json.dumps(request_body, indent=2))
        print("=== END PROMPT DEBUG ===\n\n")
        for attempt in range(3):
            try:
                resp = requests.post(self.url, json=request_body, timeout=(10, 300))
                data = resp.json()

                # Chat-style response
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

                # LM Studio error format
                if "error" in data:
                    return {
                        "error": True,
                        "message": data["error"],
                        "LLM": "",
                        "thought": "LM Studio error",
                    }

                # Unexpected format
                return {
                    "error": True,
                    "message": f"Unexpected LM Studio response: {data}",
                    "LLM": "",
                    "thought": "Unexpected response",
                }

            except requests.exceptions.ReadTimeout:
                if attempt == 2:
                    raise

            except Exception as e:
                return {
                    "error": True,
                    "message": str(e),
                    "LLM": "",
                    "thought": "Exception raised",
                }

    # ---------------------------------------------------------
    # Compatibility wrapper for tools expecting llm.complete()
    # ---------------------------------------------------------
    def complete(self, prompt: str, temperature: float = 0.0) -> str:
        """
        Tools (including fundamentals) call llm.complete(prompt).
        Internally maps to LMStudioLLM.run().
        Returns a *string*, not a dict.
        """
        result = self.run(prompt)

        if isinstance(result, dict):
            # Prefer "answer", fallback to "LLM"
            return (
                result.get("answer")
                or result.get("LLM")
                or str(result)
            )

        return str(result)
