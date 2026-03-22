from abc import ABC, abstractmethod
from typing import Dict, Optional

class LLMClient(ABC):
    """
    Abstract base class for communicating with LLM APIs.
    Subclasses must implement the _send_request method.
    """

    def __init__(self, api_key: str, api_url: Optional[str] = None):
        self.api_key = api_key
        self.api_url = api_url

    def query(self, prompt: str, **kwargs) -> str:
        """
        Generic method to query the model and return its response.
        kwargs can include API-specific parameters like max_tokens, temperature, etc.
        """
        return self._send_request(prompt, **kwargs)

    @abstractmethod
    def _send_request(self, prompt: str, **kwargs) -> str:
        """
        Send a request to the underlying LLM API and return the response as a string.
        Must be implemented by subclasses.
        """
        pass
