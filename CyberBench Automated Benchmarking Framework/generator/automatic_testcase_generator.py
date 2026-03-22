import json
from itertools import combinations, cycle
from math import ceil
import random
from typing import List, Any, Optional

import yaml

from algorithms.best_of_n import BestOfN
from benchmarks.cyberbench.cyberbench_dataset_connector import CyberBenchDataSetConnector
from models.testcase import TestCase
from models.baseprompt import BasePrompt
from utils.category_utils import expand_categories
from utils.cyberbench_strategy_taxonomy_mapping import strategy_taxonomy_mapping
from generator.testcase_generator import TestCaseGenerator
from generator.template_based import PromptTemplater


class AutomaticTestCaseGenerator(TestCaseGenerator):
    def __init__(self):
        """
        Initializes connectors for base prompts and templates.
        """
        self.benchmark_base_prompts = CyberBenchDataSetConnector()
        self.benchmark_templates = PromptTemplater()

    @staticmethod
    def generate_combinations(strategies: List[str]) -> List[tuple]:
        """
        Generate all valid single and double combinations of strategies.
        """
        singles = list(combinations(strategies, 1))
        doubles = list(combinations(strategies, 2))
        combos = singles + doubles
        random.shuffle(combos)
        return combos

    def generate_to_array(
            self,
            categories: List[Any],
            template_strategies: List[Any],
            testcases_per_category: int,
            base_prompts: Optional[List[BasePrompt]] = None,
    ) -> List[TestCase]:
        """
        Generate test cases for given categories and strategies.

        Args:
            categories: List of categories
            template_strategies: Strategies to apply
            testcases_per_category: Number of test cases per category
            base_prompts: Optional manually provided BasePrompts

        Returns:
            List of generated TestCase objects
        """
        test_cases: List[TestCase] = []

        # Handle empty strategies → no templates applied
        if not template_strategies:
            all_combos = [()]  # single empty tuple meaning "no strategy"
        else:
            print(template_strategies)
            all_combos = self.generate_combinations(template_strategies)
            print(all_combos)
        for category in categories:
            if base_prompts is None:
                category_base_prompts = self.benchmark_base_prompts.get_base_prompts(category=category)
            else:
                category_base_prompts = base_prompts

            if not category_base_prompts:
                continue  # skip if no prompts available

            random.shuffle(category_base_prompts)

            # Cycle through both prompts and combos
            base_cycle = cycle(category_base_prompts)
            combo_cycle = cycle(all_combos)

            category_testcases: List[TestCase] = []

            for i in range(testcases_per_category):
                base_prompt = next(base_cycle)
                combo = next(combo_cycle)

                if combo:  # strategies present
                    result = self.benchmark_templates.apply_templates(
                        base_prompt,
                        strategies=list(combo),
                        sample_size=1,
                    )
                    applied_strategies = list(combo)
                else:  # no strategies → just use the base prompt
                    result = [base_prompt.prompt]
                    applied_strategies = []

                expanded_categories = expand_categories(
                    base_prompt.categories,
                    applied_strategies,
                    strategy_taxonomy_mapping,
                )

                category_testcases.append(
                    TestCase(
                        id=len(test_cases) + len(category_testcases),
                        categories=expanded_categories,
                        base_prompt=base_prompt.prompt,
                        applied_strategies=applied_strategies,
                        testcase=result[0],
                        mutated_testcases=BestOfN(
                            prompt=result[0], sample_size=10
                        ).generate_variations(),
                    )
                )

            # Exactly X per category
            test_cases.extend(category_testcases)

        return test_cases

    def generate_to_json(
        self,
        categories: List[Any],
        template_strategies: List[Any],
        testcases_per_category: int,
        file_path: str,
    ) -> List[TestCase]:
        """
        Save generated test cases to a JSON file.
        """

        test_cases = self.generate_to_array(
                        categories,
                        template_strategies,
                        testcases_per_category=testcases_per_category,
                    )

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                [
                    tc.__dict__
                    for tc in test_cases
                ],
                f,
                ensure_ascii=False,
                indent=2,
            )

        return test_cases

    def generate_to_yaml(
        self,
        categories: List[Any],
        template_strategies: List[Any],
        testcases_per_category: int,
        file_path: str,
    ) -> List[TestCase]:
        """
        Save generated test cases to a YAML file.
        """

        test_cases = self.generate_to_array(
                        categories,
                        template_strategies,
                        testcases_per_category,
                    )

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                [
                    tc.__dict__
                    for tc in test_cases
                ],
                f,
                allow_unicode=True,
                sort_keys=False,
            )

        return test_cases
