import json
from typing import List
import re

import yaml

from evaluator.testcase_evaluator import TestCaseEvaluator
from models.testcase import TestCase


class RegexEvaluator(TestCaseEvaluator):
    def evaluate_to_array(self, test_cases: List[TestCase], regex) -> List[TestCase]:
        pattern = re.compile(regex, re.IGNORECASE)
        for tc in test_cases:
            if tc.response and pattern.search(tc.response):
                tc.evaluation = 1
            else:
                tc.evaluation = 0
        return test_cases

    def evaluate_to_json(self, test_cases: List[TestCase], file_path, regex, **kwargs) -> List[TestCase]:
        test_cases = self.evaluate_to_array(test_cases, regex)
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

    def evaluate_to_yaml(self, test_cases: List[TestCase], file_path, regex, **kwargs) -> List[TestCase]:
        test_cases = self.evaluate_to_array(test_cases, regex)
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