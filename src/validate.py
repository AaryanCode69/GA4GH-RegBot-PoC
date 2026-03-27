"""
src/validate.py  -  Phase 5: Deterministic Validation Layer
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from llama_index.core.schema import NodeWithScore

from config import REQUIRED_OUTPUT_FIELDS, VALID_SEVERITY_VALUES


def validate_output(
    raw_json: str,
    context_nodes: list[NodeWithScore],
) -> dict[str, Any]:
    """
    Deterministically validate the LLM JSON output from Phase 4.

    Runs four checks in order:
      1. raw_json is valid JSON
      2. All required fields are present
      3. severity is one of: low | medium | high
      4. exact_quote is a verbatim substring of the retrieved source text

    Returns the parsed dict with two fields appended:
      - validation_passed  : bool
      - validation_errors  : list[str]  (empty when validation_passed is True)

    Zero LLM calls. Fully deterministic.
    """
    errors: list[str] = []
    parsed: dict[str, Any] = {}

    # Check 1: valid JSON
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        errors.append(f"JSON parse error: {exc}")
        return _failed(parsed, errors)

    # Check 2: required fields present
    missing = REQUIRED_OUTPUT_FIELDS - parsed.keys()
    if missing:
        errors.append(f"Missing required fields: {sorted(missing)}")

    # Check 3: severity value valid
    severity = parsed.get("severity", "")
    if severity not in VALID_SEVERITY_VALUES:
        errors.append(
            f"Invalid severity {severity!r}. Must be one of: {sorted(VALID_SEVERITY_VALUES)}"
        )

    # Check 4: exact_quote is a verifiable substring of the retrieved source text
    exact_quote = parsed.get("exact_quote", "")
    source_text = "\n".join(n.node.get_content() for n in context_nodes)

    if not exact_quote:
        errors.append("exact_quote is empty.")
    elif exact_quote not in source_text:
        errors.append(
            "exact_quote not found verbatim in retrieved source text. "
            "Citation cannot be verified."
        )

    passed = len(errors) == 0

    print(f"[validate] validation_passed : {passed}")
    if errors:
        for err in errors:
            print(f"[validate]   ✗ {err}")
    else:
        print("[validate]   ✓ All checks passed")
    print()

    return {**parsed, "validation_passed": passed, "validation_errors": errors}


def _failed(parsed: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    """Return a failed validation result when parsing itself fails."""
    return {**parsed, "validation_passed": False, "validation_errors": errors}


if __name__ == "__main__":
    from config import SAMPLE_PDF_PATH
    from src.generate import generate_finding
    from src.index import build_index
    from src.ingest import load_pdf
    from src.retrieve import retrieve_context

    MOCK_QUERY = (
        "Does the data use agreement require informing data subjects about "
        "cross-jurisdictional sharing and the applicable legal frameworks?"
    )

    print("[validate] Running standalone Phase 5 test...\n")
    pages = load_pdf(SAMPLE_PDF_PATH)
    index, storage_context = build_index(pages)
    nodes = retrieve_context(MOCK_QUERY, index, storage_context)
    raw_json = generate_finding(MOCK_QUERY, nodes)
    result = validate_output(raw_json, nodes)

    print("=" * 62)
    print("FINAL VALIDATED OUTPUT")
    print("=" * 62)
    print(json.dumps(result, indent=2))
    print("=" * 62)
    status = "PASSED ✓" if result["validation_passed"] else "FAILED ✗"
    print(f"Phase 5 complete — Validation {status}")
    print("=" * 62)
