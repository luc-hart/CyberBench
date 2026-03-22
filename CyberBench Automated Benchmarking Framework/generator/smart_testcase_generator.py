import json
from itertools import combinations, cycle
import random
from typing import List

import yaml

from algorithms.best_of_n import BestOfN
from benchmarks.cyberbench.cyberbench_dataset_connector import CyberBenchDataSetConnector
from llms.LLMClient import LLMClient
from models.testcase import TestCase
from generator.smart_components.SmartBasePromptGenerator import SmartBasePromptGenerator
from generator.smart_components.SmartTaxonomyMapper import SmartTaxonomyMapper
from benchmarks.cyberbench.template_strategies import EFFECTIVE_TEMPLATE_STRATEGIES
from utils.category_utils import expand_categories
from utils.cyberbench_strategy_taxonomy_mapping import strategy_taxonomy_mapping
from generator.testcase_generator import TestCaseGenerator
from generator.template_based import PromptTemplater


class SmartTestCaseGenerator(TestCaseGenerator):
    def __init__(self, llm: LLMClient):
        """
        Initializes connectors for base prompts and templates.
        """
        self.llm = llm
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

    @staticmethod
    def effective_combinations() -> List[tuple]:
        return [
            ('system_mode', 'payload_splitting'),
            ('payload_splitting',),
            ('system_mode',),
            ('system_mode', 'virtualization'),
            ('output_formatting_manipulation', 'repeated_token_attack'),
            ('ignore_previous_instructions', 'repeated_token_attack')
        ]

    def generate_to_array(
            self,
            objective: str,
            context: str,
            testcases_per_category: int = None,
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
        categories = SmartTaxonomyMapper(self.llm).get_categories_from_objective_and_context(objective, context)
        print(f"[DEBUG] SmartTestCaseGenerator: Categories: {categories}")
        # Handle empty strategies → no templates applied
        #all_combos = self.generate_combinations(EFFECTIVE_TEMPLATE_STRATEGIES)
        #print(all_combos)
        all_combos = self.effective_combinations()
        for category in categories:
            category_base_prompts = SmartBasePromptGenerator(self.llm, self.benchmark_base_prompts).generate_base_prompts(category, testcases_per_category, objective, context)
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
                print(f"[DEBUG] SmartTestCaseGenerator: base_prompt.categories = {base_prompt.categories}")
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
            objective: str,
            context: str,
            testcases_per_category: int,
            file_path: str
    ) -> List[TestCase]:
        """
        Save generated test cases to a JSON file.
        """

        test_cases = self.generate_to_array(
                        objective=objective,
                        context=context,
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
            objective: str,
            context: str,
            testcases_per_category: int,
            file_path: str,
    ) -> List[TestCase]:
        """
        Save generated test cases to a YAML file.
        """

        test_cases = self.generate_to_array(
                        objective=objective,
                        context=context,
                        testcases_per_category=testcases_per_category,
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
