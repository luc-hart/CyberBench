import json
import yaml
from typing import List
from algorithms.best_of_n import BestOfN
from models.testcase import TestCase
from models.baseprompt import BasePrompt
from generator.testcase_generator import TestCaseGenerator
from generator.template_based import PromptTemplater


class ManualTestCaseGenerator(TestCaseGenerator):
    def __init__(self):
        """
        Stateless _generator; all configs are passed to generate_to_array.
        """
        self.templater = PromptTemplater()

    def generate_to_array(
        self,
        base_prompt: BasePrompt,
        strategies: List[str],
        sample_size: int
    ) -> List[TestCase]:
        """
        Generate test cases using the provided BasePrompt, strategies, and sample size.
        Categories are ignored in manual mode.
        """
        test_cases: List[TestCase] = []

        # Repeat the base prompt sample_size times
        for i in range(sample_size):
            prompt_text = base_prompt.prompt
            applied_strategies = strategies if strategies else []

            if applied_strategies:
                # Apply all strategies at once, preserving the order
                result = self.templater.apply_templates(
                    base_prompt,
                    strategies=applied_strategies,
                    sample_size=1
                )
                prompt_text = result[0]

            test_cases.append(
                TestCase(
                    id=len(test_cases),
                    categories=[],  # empty since manual ignores categories
                    base_prompt=base_prompt.prompt,
                    applied_strategies=applied_strategies,
                    testcase=prompt_text,
                    mutated_testcases=BestOfN(prompt=prompt_text, sample_size=10).generate_variations()
                )
            )

        return test_cases

    def generate_to_json(
        self,
        base_prompt: BasePrompt,
        strategies: List[str],
        sample_size: int,
        file_path: str
    ) -> List[TestCase]:
        """
        Save generated test cases to a JSON file.
        """

        test_cases = self.generate_to_array(base_prompt, strategies, sample_size)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                [tc.__dict__ for tc in test_cases],
                f,
                ensure_ascii=False,
                indent=2
            )
        return test_cases

    def generate_to_yaml(
        self,
        base_prompt: BasePrompt,
        strategies: List[str],
        sample_size: int,
        file_path: str
    ) -> None:
        """
        Save generated test cases to a YAML file.
        """

        test_cases = self.generate_to_array(base_prompt, strategies, sample_size)

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                [tc.__dict__ for tc in test_cases],
                f,
                allow_unicode=True,
                sort_keys=False
            )

        return test_cases
