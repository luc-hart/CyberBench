import requests
from typing import Optional, Dict, Any
from models.testcase import TestCase
from .target_api import TargetAPI  # your abstract class


class GenericTarget(TargetAPI):
    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.headers = headers or {"Content-Type": "application/json"}
        if api_key and "Authorization" not in self.headers:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def build_payload(self, system_prompt, user_prompt, **gen_params) -> Dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        payload = {"messages": messages}
        payload.update(gen_params)
        return payload

    def query_llm(self, user_prompt: str, system_prompt: Optional[str] = None, **gen_params: Any) -> str:
        """Send a query to the target LLM API and return the response text."""
        payload = self.build_payload(system_prompt, user_prompt, **gen_params)
        resp = requests.post(self.api_url, headers=self.headers, json=payload)

        if resp.status_code == 400:
            return "Response filtered."

        resp.raise_for_status()
        data = resp.json()

        # Normalize return field
        if "output" in data:
            return data["output"]
        elif "response" in data:
            return data["response"]
        elif "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
            elif "text" in choice:
                return choice["text"]
        return str(data)

