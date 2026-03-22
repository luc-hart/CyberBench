from abc import ABC, abstractmethod
from typing import List

from models.baseprompt import BasePrompt
from models.taxonomy import Taxonomy


class Benchmark(ABC):
    name: str
    taxonomy: Taxonomy

    def taxonomy(self) -> Taxonomy:
        return self.taxonomy

    def get_base_prompts(self, category, sample_size) -> List[BasePrompt]:
        return [BasePrompt(
            prompt_goal="",
            prompt_object="",
            prompt="",
            categories = []
        )]

