import requests
from typing import List, Dict, Optional

from llms.LLMClient import LLMClient


class DeepSeekClient(LLMClient):
    """
    DeepSeek Chat Completions client.
    """


    def _send_request(
        self,
        prompt: str,
        messages: Optional[List[Dict]] = None,
        model: str = "deepseek-chat",
        max_tokens: int = 4096,
        temperature: float = 1.0,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[List[str]] = None,
        response_format: Dict = {"type": "text"},
        stream: bool = False,
        tools: Optional[List] = None,
        tool_choice: str = "none",
        logprobs: bool = False,
        top_logprobs: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send a chat-completion request to DeepSeek API.
        All parameters map directly to DeepSeek's API options.
        """
        url = self.api_url or "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if messages is None:
            messages = [{"role": "user", "content": prompt}]

        payload: Dict = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stop": stop,
            "response_format": response_format,
            "stream": stream,
            "tools": tools,
            "tool_choice": tool_choice,
            "logprobs": logprobs,
            "top_logprobs": top_logprobs,
            **kwargs
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # Return text from choices[0].message.content
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return str(data)
