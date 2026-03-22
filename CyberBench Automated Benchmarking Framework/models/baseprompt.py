from dataclasses import dataclass, asdict
from typing import List, Any, Optional
import json
import yaml  # pip install pyyaml

@dataclass
class BasePrompt:
    prompt: str
    prompt_goal: str
    prompt_object: str
    categories: List[Any] = None

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_yaml(self):
        return yaml.dump(self.to_dict(), allow_unicode=True)
