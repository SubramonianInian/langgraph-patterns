"""Load prompts from a pattern's prompts.yml.

Each pattern keeps its prompts next to its code — ``patterns/X/prompts.yml`` —
so copying a pattern folder into another project brings the prompts along.

Usage inside a pattern's ``graph.py``:

    from shared.prompts import load

    PROMPTS = load(__file__)
    prompt = PROMPTS["supervisor"].format(question=state["question"])
"""

from pathlib import Path
from typing import Any

import yaml


def load(caller_file: str) -> dict[str, Any]:
    """Read prompts.yml from the same directory as the caller."""
    path = Path(caller_file).parent / "prompts.yml"
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a top-level mapping, got {type(data).__name__}")
    return data
