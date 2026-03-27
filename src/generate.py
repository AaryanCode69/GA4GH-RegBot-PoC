
from __future__ import annotations

from typing import Any


def generate_finding(query: str, context_nodes: list[Any]) -> str:
    raise NotImplementedError("Phase 4 (generate.py) is not yet implemented.")




def _build_context_block(context_nodes: list[Any]) -> str:
    raise NotImplementedError


def _build_prompt(query: str, context_block: str) -> str:
    raise NotImplementedError


def _strip_markdown_fences(raw: str) -> str:
    raise NotImplementedError



if __name__ == "__main__":
