from dataclasses import dataclass, asdict, field
from typing import List, Optional
import json
import yaml  # pip install pyyaml

@dataclass
class Category:
    name: str
    slug: str
    description: Optional[str] = None
    one_point_evaluation_question: Optional[str] = None
    half_point_evaluation_question: Optional[str] = None
    zero_point_evaluation_question: Optional[str] = None
    subcategories: List["Category"] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        subcats = [cls.from_dict(c) for c in data.get("subcategories", [])]
        return cls(
            name=data["name"],
            slug=data.get("slug", ""),
            description=data.get("description"),
            one_point_evaluation_question=data.get("one_point_evaluation_question"),
            half_point_evaluation_question=data.get("half_point_evaluation_question"),
            zero_point_evaluation_question=data.get("zero_point_evaluation_question"),
            subcategories=subcats
        )
