from __future__ import annotations

from typing import Any


def retrieve_context(
    query: str,
    index: Any,
    storage_context: Any,
    top_k: int | None = None,
) -> list[Any]:

    raise NotImplementedError(
        "Phase 3 (retrieve.py) is not yet implemented. "
        "Complete Phase 2 (index.py) first, then implement retrieve_context()."
    )
