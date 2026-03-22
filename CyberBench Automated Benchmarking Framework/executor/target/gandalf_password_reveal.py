import requests
from typing import Optional, Dict, List
from models.testcase import TestCase
from .target_api import TargetAPI  # your abstract class


class GandalfPasswordReveal(TargetAPI):
    def __init__(
        self,
        defender_level: int = 1,
        headers: Optional[Dict[str, str]] = None
    ):
        self.base_url = "https://gandalf-api.lakera.ai/api"
        self.defender_level = defender_level
        self.defender_types = {
            1: "baseline",
            2: "do-not-tell",
            3: "do-not-tell-and-block",
            4: "gpt-is-password-encoded",
            5: "word-blacklist",
            6: "gpt-blacklist",
            7: "gandalf",
        }
        self.headers = headers or {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'gandalf-api.lakera.ai',
            'Origin': 'https://gandalf.lakera.ai',
            'Pragma': 'no-cache',
            'Referer': 'https://gandalf.lakera.ai/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0'
        }

    def query_llm(self, testcase_text: str) -> str:
        url = f"{self.base_url}/send-message"

        # multipart/form-data payload
        files = {
            "defender": (None, self.defender_types[self.defender_level]),
            "prompt": (None, testcase_text)
        }

        try:
            response = requests.post(url, files=files, headers=self.headers)
            response.raise_for_status()
            return response.json().get("answer", "")
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")
        except ValueError:
            raise RuntimeError(f"Invalid JSON response: {response.text}")

    def get_responses_from_testcases_array(self, testcases: List[TestCase]) -> List[TestCase]:
        """Fill each TestCase.response using its .testcase attribute"""
        for tc in testcases:
            tc.response = self.query_llm(tc.testcase)
            print(tc.response)
        return testcases

    def get_responses_from_testcases_json(self, file_path: str) -> List[TestCase]:
        import json
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        testcases = [TestCase(**tc) for tc in data]
        return self.get_responses_from_testcases_array(testcases)

    def get_responses_from_testcases_yaml(self, file_path: str) -> List[TestCase]:
        import yaml
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        testcases = [TestCase(**tc) for tc in data]
        return self.get_responses_from_testcases_array(testcases)

    def set_defender_level(self, level: int):
        if level not in self.defender_types:
            raise ValueError("Invalid defender level. Must be between 1-7")
        self.defender_level = level
