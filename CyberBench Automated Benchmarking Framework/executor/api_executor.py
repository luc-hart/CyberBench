import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict

import yaml

from executor.executor import Executor
from models.testcase import TestCase
from executor.target.generic_target import GenericTarget


class APIExecutor(Executor):
    def __init__(self,
                 api_url: str,
                 headers: Optional[Dict[str, str]]
                 ):
        self.target = GenericTarget(api_url=api_url, headers=headers)

    def execute_to_array(self, test_cases: List[TestCase], threads=1, **kwargs) -> List[TestCase]:
        results = []
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # store (i, test_case) so unpacking works later
            future_to_case = {
                executor.submit(self.target.query_llm, test_case.testcase, **kwargs): (i, test_case)
                for i, test_case in enumerate(test_cases, start=1)
            }

            for future in as_completed(future_to_case):
                i, test_case = future_to_case[future]
                print(f"[DEBUG] APIExecutor: Executing testcase #{i}: {test_case.testcase}")
                try:
                    response = future.result()
                    print(f"[DEBUG] APIExecutor: Received response for testcase #{i}: {response}")
                    test_case.response = response
                except Exception as e:
                    print(f"[ERROR] APIExecutor: {e}")
                    test_case.response = f"ERROR: {e}"
                results.append(test_case)

        return results

    def execute_to_json(self, test_cases: List[TestCase], file_path: str, **kwargs) -> List[TestCase]:
        results = self.execute_to_array(test_cases, **kwargs)
        data = [tc.__dict__ for tc in results]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return results

    def execute_to_yaml(self, test_cases: List[TestCase], file_path: str, **kwargs) -> List[TestCase]:
        results = self.execute_to_array(test_cases, **kwargs)
        data = [tc.__dict__ for tc in results]
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True)
        return results
