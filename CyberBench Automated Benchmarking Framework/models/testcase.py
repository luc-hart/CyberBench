from dataclasses import dataclass, asdict
from typing import List, Optional, Any
import json
import yaml  # pip install pyyaml

@dataclass
class TestCase:
    id: int
    base_prompt: str
    categories: List[Any]
    applied_strategies: List[str]
    testcase: str
    mutated_testcases: List[str]
    response: Optional[str] = None      # optional, defaults to None
    evaluation: Optional[str] = None    # optional, defaults to None

    # --- Serialization Methods ---
    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), allow_unicode=True)

    # --- Deserialization / Factory Methods ---
    @classmethod
    def from_dict(cls, data: dict, id: Optional[int] = None) -> "TestCase":
        return cls(
            id=id if id is not None else data.get("id", 0),
            base_prompt=data.get("base_prompt", ""),
            categories=data.get("categories", []),
            applied_strategies=data.get("applied_strategies", []),
            testcase=data.get("testcase", ""),
            mutated_testcases=data.get("mutated_testcases", []),
            response=data.get("response"),
            evaluation=data.get("evaluation"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> List["TestCase"]:
        data_list = json.loads(json_str)
        return [cls.from_dict(tc_dict, id=i) for i, tc_dict in enumerate(data_list)]

    @classmethod
    def from_yaml(cls, yaml_str: str) -> List["TestCase"]:
        data_list = yaml.safe_load(yaml_str)
        return [cls.from_dict(tc_dict, id=i) for i, tc_dict in enumerate(data_list)]
