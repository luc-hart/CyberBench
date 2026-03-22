from abc import ABC, abstractmethod
from typing import List

from models.testcase import TestCase


class TargetAPI(ABC):
    @abstractmethod
    def query_llm(self, **kwargs) -> str:
        """Generate target response and return it as a string"""
        pass