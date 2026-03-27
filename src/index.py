from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from llama_index.core import StorageContext, VectorStoreIndex


def build_index(
    pages: list[dict[str, Any]],
) -> tuple["VectorStoreIndex", "StorageContext"]:
    raise NotImplementedError(
        "Phase 2 (Hierarchical Chunking & Indexing) is not yet implemented.\n"
        "See the TODO block in src/index.py for the full implementation plan."
    )


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))

    from config import SAMPLE_PDF_PATH
    from src.ingest import load_pdf

    print("[index] Running standalone Phase 2 test...\n")
    pages = load_pdf(SAMPLE_PDF_PATH)
    index, storage_context = build_index(pages)

    print("\n[index] ✓ Index built successfully.")
    print(f"[index]   Docstore node count : {len(storage_context.docstore.docs)}")
