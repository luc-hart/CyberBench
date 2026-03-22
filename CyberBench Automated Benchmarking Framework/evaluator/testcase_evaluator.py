from abc import ABC, abstractmethod
from typing import List

from models.testcase import TestCase


class TestCaseEvaluator(ABC):
    @abstractmethod
    def evaluate_to_array(self, **kwargs) -> List[TestCase]:
        """Generate output and return it as a list"""
        pass

    @abstractmethod
    def evaluate_to_json(self, **kwargs) -> List[TestCase]:
        """Generate output and write it to a file"""
        pass

    @abstractmethod
    def evaluate_to_yaml(self, **kwargs) -> List[TestCase]:
        """Generate output and write it to a file"""
        pass
