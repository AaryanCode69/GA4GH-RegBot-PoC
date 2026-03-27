

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import REQUIRED_OUTPUT_FIELDS, VALID_SEVERITY_VALUES



def validate_output(
    raw_json: str,
    context_nodes: list[Any],
) -> dict[str, Any]:

    raise NotImplementedError("Phase 5 not yet implemented.")




if __name__ == "__main__":
