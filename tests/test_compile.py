"""Smoke tests: every pattern's graph imports, loads its prompts, and compiles.

Deliberately no LLM calls here — these tests catch import errors, prompt-file
typos, and LangGraph API drift without burning tokens or needing a key.
"""

import importlib
import os

import pytest

# LangChain provider clients sometimes validate keys at construction time.
# The tests never actually call a model, but set a placeholder so imports
# don't trip over missing-credential checks.
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test-placeholder")

PATTERN_MODULES = [
    "patterns.router.graph",
    "patterns.reflect_retry.graph",
    "patterns.hitl.graph",
    "patterns.plan_execute.graph",
    "patterns.map_reduce.graph",
    "patterns.memory.graph",
    "patterns.tool_guardrails.graph",
    "patterns.self_heal.graph",
]


@pytest.mark.parametrize("module_name", PATTERN_MODULES)
def test_pattern_compiles(module_name: str) -> None:
    module = importlib.import_module(module_name)
    graph = module.build_graph()
    assert graph is not None, f"{module_name}.build_graph() returned None"


@pytest.mark.parametrize("module_name", PATTERN_MODULES)
def test_pattern_has_prompts(module_name: str) -> None:
    module = importlib.import_module(module_name)
    assert hasattr(module, "PROMPTS"), f"{module_name} did not load a PROMPTS mapping"
    assert isinstance(module.PROMPTS, dict), f"{module_name}.PROMPTS is not a dict"
    assert module.PROMPTS, f"{module_name}.PROMPTS is empty"
