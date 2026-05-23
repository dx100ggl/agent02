import requests
from brain.c4.tools.base import Tool


class LMStudioLLM(Tool):
    """
    C4 tool that sends prompts to LM Studio's local server.
    """

    def __init__(self,
                 name="lmstudio_llm",
                 url="http://192.168.0.80:1234/v1/chat/completions",
                 model="local-model"):
        super().__init__(name=name)
        self.url = url
        self.model = model

    def run(self, prompt: str):
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }

        try:
            resp = requests.post(self.url, json=payload, timeout=30)
            data = resp.json()

            # 1. Chat-style response
            if "choices" in data and data["choices"]:
                choice = data["choices"][0]

                # Chat format
                if "message" in choice and "content" in choice["message"]:
                    return {"final": True, "answer": choice["message"]["content"]}

                # Text completion format
                if "text" in choice:
                    return {"final": True, "answer": choice["text"]}

            # 2. LM Studio sometimes returns errors in JSON
            if "error" in data:
                return {"error": True, "message": data["error"]}

            # 3. Unexpected format
            return {"error": True, "message": f"Unexpected LM Studio response: {data}"}

        except Exception as e:
            return {"error": True, "message": str(e)}
