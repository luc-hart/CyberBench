from dataclasses import dataclass, asdict, field
from typing import List, Optional
import json
import yaml  # pip install pyyaml

from models.category import Category


@dataclass
class Taxonomy:
    name: str
    categories: List[Category]

    def to_dict(self):
        return {"categories": [c.to_dict() for c in self.categories]}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), allow_unicode=True)

    def to_nested_dict(self) -> dict:
        """
        Convert taxonomy to nested dict format:
        {benchmark_name: {category: {subcategory: [leaves...]}}}
        """

        def recurse(cats: List[Category]):
            out = {}
            for c in cats:
                if c.subcategories:
                    # recursive nesting
                    out[c.name] = recurse(c.subcategories)
                else:
                    # leaf node, append to list
                    out.setdefault("_leaves", []).append(c.name)
            # If only leaves, unwrap _leaves to simple list
            if set(out.keys()) == {"_leaves"}:
                return out["_leaves"]
            return out

        return {self.name: recurse(self.categories)}

    def get_category_by_name(self, name: str) -> Optional[Category]:
        def recurse(cats: List[Category]) -> Optional[Category]:
            for c in cats:
                if c.name == name:
                    return c
                found = recurse(c.subcategories)
                if found:
                    return found
            return None

        return recurse(self.categories)

    def get_category_by_slug(self, slug: str) -> Optional[Category]:
        def recurse(cats: List[Category]) -> Optional[Category]:
            for c in cats:
                if c.slug == slug:
                    return c
                found = recurse(c.subcategories)
                if found:
                    return found
            return None

        return recurse(self.categories)


    @classmethod
    def from_dict(cls, data: dict, taxonomy_name: str) -> "Taxonomy":
        cls.name = taxonomy_name
        categories = [Category.from_dict(c) for c in data.get("categories", [])]
        return cls(categories=categories, name=taxonomy_name)

    @classmethod
    def from_json(cls, path: str, taxonomy_name: str) -> "Taxonomy":
        cls.name = taxonomy_name
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data, taxonomy_name)

    @classmethod
    def from_yaml(cls, path: str, taxonomy_name: str) -> "Taxonomy":
        cls.name = taxonomy_name
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data, taxonomy_name)