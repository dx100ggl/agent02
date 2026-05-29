# brain/c4/tools/builtin/lmstudio_llm.py

from __future__ import annotations

import requests
from typing import Any, Dict, Union

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
        """
        Accepts either:
            - "plain string"
            - {"text": "...", "memory_context": "..."}

        Produces a single user-facing prompt string.
        """
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
        full_prompt = self._build_prompt(payload)

        request_body = {
            "model": self.model,
            "messages": [{"role": "user", "content": full_prompt}],
            "temperature": 0.7,
        }

        try:
            resp = requests.post(self.url, json=request_body, timeout=30)
            data = resp.json()

            # -----------------------------------------------------
            # 1. Chat-style response
            # -----------------------------------------------------
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

            # -----------------------------------------------------
            # 2. LM Studio error format
            # -----------------------------------------------------
            if "error" in data:
                return {
                    "error": True,
                    "message": data["error"],
                    "LLM": "",
                    "thought": "LLM error",
                }

            # -----------------------------------------------------
            # 3. Unexpected format
            # -----------------------------------------------------
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
