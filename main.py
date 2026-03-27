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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))

from config import SAMPLE_PDF_PATH
from src.index import build_index  # Phase 2  ✅
from src.ingest import load_pdf  # Phase 1  ✅

# from src.retrieve import retrieve_context          # Phase 3  ⏳
# from src.generate import generate_finding          # Phase 4  ⏳
# from src.validate import validate_output           # Phase 5  ⏳

MOCK_QUERY: str = (
    "Does the data use agreement require informing data subjects about "
    "cross-jurisdictional sharing and the applicable legal frameworks?"
)


def main() -> None:
    print("\n" + "=" * 65)
    print("  GA4GH-RegBot PoC – Local-First Compliance Pipeline")
    print("=" * 65 + "\n")

    # Phase 1: Ingestion
    print("[main] ── Phase 1: Ingestion & Parsing ──────────────────────")
    pages = load_pdf(SAMPLE_PDF_PATH)
    print(f"[main]    {len(pages)} page(s) ingested successfully.\n")

    # Phase 2: Hierarchical Indexing
    print("[main] ── Phase 2: Hierarchical Chunking & Indexing ─────────")
    index, storage_context = build_index(pages)
    print("[main]    Index built and persisted to ChromaDB.\n")

    # Phase 3: Small-to-Big Retrieval
    # print("[main] ── Phase 3: Small-to-Big Retrieval ──────────────────")
    # print(f"[main]    Query: {MOCK_QUERY!r}")
    # context_nodes = retrieve_context(MOCK_QUERY, index, storage_context)
    # print(f"[main]    {len(context_nodes)} parent context node(s) retrieved.\n")

    # Phase 4: Guardrailed Generation
    # print("[main] ── Phase 4: Guardrailed Generation ───────────────────")
    # raw_json = generate_finding(MOCK_QUERY, context_nodes)
    # print(f"[main]    Raw LLM output:\n{raw_json}\n")

    # Phase 5: Deterministic Validation
    # print("[main] ── Phase 5: Deterministic Citation Validation ────────")
    # result = validate_output(raw_json, context_nodes)
    # print("\n[main]    Final validated output:")
    # print(json.dumps(result, indent=2))

    print("=" * 65)
    print("[main] Pipeline run complete.")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
