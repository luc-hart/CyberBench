import requests
from typing import Optional, Dict, Any
from llms.LLMClient import LLMClient

class GenericLLMClient(LLMClient):
    """
    Generic LLM client with flexible headers, API URL, model, and parameters.
    Supports APIs where the API key may be provided in headers (e.g., Authorization, Cookie, etc.).
    Model is optional; if not provided, the API default is used.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
        default_model: Optional[str] = None,
        timeout: int = 30
    ):
        super().__init__(api_key or "", api_url)
        self.default_headers = default_headers
        self.default_model = default_model
        self.timeout = timeout

    def build_payload(self, system_prompt: Optional[str], user_prompt: str, **gen_params) -> Dict[str, Any]:
        """
        Build the LLM request payload.
        system_prompt: optional system-level prompt
        user_prompt: the user prompt
        gen_params: additional generation parameters (temperature, max_tokens, model, etc.)
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        payload = {"messages": messages}
        payload.update(gen_params)
        return payload

    def _send_request(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        Send a request to the LLM API and return the response text.
        Optional parameters:
            - model: model name (uses default_model if not provided)
            - headers: custom HTTP headers
            - api_url: override API endpoint
            - temperature, max_tokens, etc.: any model-specific parameters
        """
        headers = kwargs.pop("headers", self.default_headers)
        api_url = kwargs.pop("api_url", self.api_url)
        model = kwargs.pop("model", self.default_model)

        if not api_url:
            raise ValueError("api_url must be provided either at init or via kwargs.")
        if headers is None:
            raise ValueError("headers must be provided either at init or via kwargs.")

        if model is not None:
            kwargs["model"] = model

        payload = self.build_payload(system_prompt=system_prompt, user_prompt=prompt, **kwargs)

        response = requests.post(api_url, headers=headers, json=payload, timeout=self.timeout)

        # Handle filtered response
        if response.status_code == 400:
            return "Response filtered."

        response.raise_for_status()
        data = response.json()

        # Flexible extraction
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