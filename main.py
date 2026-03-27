"""
main.py – GA4GH-RegBot PoC Pipeline Orchestrator

Runs all 5 phases in sequence:
    Phase 1 : Ingest PDF (PyMuPDF)
    Phase 2 : Build hierarchical index (LlamaIndex + ChromaDB)
    Phase 3 : Retrieve relevant context (small-to-big)
    Phase 4 : Generate guardrailed findings (Ollama)
    Phase 5 : Validate citations deterministically

Usage:
    python main.py
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, SAMPLE_PDF_PATH
from src.generate import generate_finding  # Phase 4  ✅
from src.index import build_index  # Phase 2  ✅
from src.ingest import load_pdf  # Phase 1  ✅
from src.retrieve import retrieve_context  # Phase 3  ✅
from src.validate import validate_output  # Phase 5  ✅

MOCK_QUERY: str = (
    "Does the data use agreement require informing data subjects about "
    "cross-jurisdictional sharing and the applicable legal frameworks?"
)


# ── Pre-flight check ──────────────────────────────────────────────────────────


def _check_ollama() -> None:
    """
    Verify the Ollama daemon is reachable and the required model is available
    before the pipeline starts. Exits with a clear message on failure.
    """
    # Step 1: connectivity
    try:
        urllib.request.urlopen(OLLAMA_BASE_URL, timeout=5)
    except urllib.error.URLError:
        print(f"[preflight] ERROR: Ollama is not reachable at {OLLAMA_BASE_URL}")
        print("[preflight]   Start the daemon : ollama serve")
        print(f"[preflight]   Pull the model  : ollama pull {OLLAMA_MODEL}")
        sys.exit(1)

    print(f"[preflight] Ollama daemon reachable at {OLLAMA_BASE_URL}  ✓")

    # Step 2: model availability  – GET /api/tags returns the local model list
    try:
        with urllib.request.urlopen(f"{OLLAMA_BASE_URL}/api/tags", timeout=5) as resp:
            data = json.loads(resp.read().decode())
        available = [m["name"] for m in data.get("models", [])]
    except Exception:
        # If the tags endpoint fails for any reason treat it as a soft warning
        print(f"[preflight] WARNING: Could not verify model list. Continuing.\n")
        return

    # Ollama may store the name with or without the full quant suffix
    model_found = any(
        OLLAMA_MODEL in name or name in OLLAMA_MODEL for name in available
    )

    if not model_found:
        print(f"[preflight] ERROR: Model '{OLLAMA_MODEL}' not found in Ollama.")
        print(f"[preflight]   Pull it with: ollama pull {OLLAMA_MODEL}")
        print(f"[preflight]   Available models: {available if available else 'none'}")
        sys.exit(1)

    print(f"[preflight] Model '{OLLAMA_MODEL}' available  ✓\n")


# ── Pipeline ──────────────────────────────────────────────────────────────────


def main() -> None:
    print("\n" + "=" * 65)
    print("  GA4GH-RegBot PoC – Local-First Compliance Pipeline")
    print("=" * 65 + "\n")

    # Pre-flight: confirm Ollama is up before doing any heavy work
    _check_ollama()

    # Phase 1: Ingestion
    print("[main] ── Phase 1: Ingestion & Parsing ──────────────────────")
    pages = load_pdf(SAMPLE_PDF_PATH)
    print(f"[main]    {len(pages)} page(s) ingested successfully.\n")

    # Phase 2: Hierarchical Indexing
    print("[main] ── Phase 2: Hierarchical Chunking & Indexing ─────────")
    index, storage_context = build_index(pages)
    print("[main]    Index built and persisted to ChromaDB.\n")

    # Phase 3: Small-to-Big Retrieval
    print("[main] ── Phase 3: Small-to-Big Retrieval ───────────────────")
    print(f"[main]    Query: {MOCK_QUERY!r}")
    context_nodes = retrieve_context(MOCK_QUERY, index, storage_context)
    print(f"[main]    {len(context_nodes)} parent context node(s) retrieved.\n")

    # Phase 4: Guardrailed Generation
    print("[main] ── Phase 4: Guardrailed Generation ───────────────────")
    raw_json = generate_finding(MOCK_QUERY, context_nodes)
    print("[main]    Raw LLM output received.\n")

    # Phase 5: Deterministic Validation
    print("[main] ── Phase 5: Deterministic Citation Validation ─────────")
    result = validate_output(raw_json, context_nodes)
    passed = result.get("validation_passed", False)
    print(f"[main]    validation_passed: {passed}")
    print("[main]    Final validated output:\n")
    print(json.dumps(result, indent=2))

    print("\n" + "=" * 65)
    print("[main] Pipeline run complete.")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
