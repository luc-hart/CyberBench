from abc import ABC, abstractmethod
from typing import List

from models.testcase import TestCase


class Executor(ABC):
    @abstractmethod
    def execute_to_array(self, **kwargs) -> List[TestCase]:
        """Generate output and return it as a list"""
        pass

    @abstractmethod
    def execute_to_json(self, **kwargs) -> List[TestCase]:
        """Generate output and write it to a file"""
        pass

    @abstractmethod
    def execute_to_yaml(self, **kwargs) -> List[TestCase]:
        """Generate output and write it to a file"""
        pass
