import requests

from llms.LLMClient import LLMClient


class OpenAIClient(LLMClient):
    """
    Implementation of LLMClient for OpenAI-compatible APIs.
    """

    def _send_request(self, prompt: str, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": kwargs.get("model", "gpt-5"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 1),
            "max_tokens": kwargs.get("max_tokens", 1000)
        }

        response = requests.post(
            self.api_url or "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
