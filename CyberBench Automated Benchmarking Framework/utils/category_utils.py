# utils/category_utils.py
from typing import List, Dict

def expand_categories(
    base_categories: List[str],
    applied_strategies: List[str],
    mapping: Dict[str, List[str]]
) -> List[List[str]]:
    """Return nested category arrays: first base, then mapped for each strategy."""
    expanded: List[List[str]] = []

    # ensure base_categories is always a list of paths (List[List[str]])
    if len(base_categories) > 1:
        expanded.append(base_categories)
    else:
        for cat in base_categories:
            expanded.append(cat)

    for strat in applied_strategies:
        mapped = mapping.get(strat)
        if mapped:
            expanded.append(mapped)

    return expanded
