"""
src/retrieve.py  -  Phase 3: Small-to-Big Retrieval
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.schema import NodeWithScore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from config import EMBED_MODEL_NAME, TOP_K_RETRIEVAL


def retrieve_context(
    query: str,
    index: VectorStoreIndex,
    storage_context: StorageContext,
    top_k: int | None = None,
) -> list[NodeWithScore]:
    """
    Retrieve the most relevant parent context nodes for a given query.

    Queries ChromaDB for top-K child nodes via vector similarity, then uses
    AutoMergingRetriever to expand child hits to their parent nodes,
    returning full legal context blocks for Phase 4 generation.

    Returns List[NodeWithScore] of expanded parent-level nodes.
    """
    effective_k = top_k if top_k is not None else TOP_K_RETRIEVAL

    # Ensure the local embed model is used for query embedding
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)

    base_retriever = index.as_retriever(similarity_top_k=effective_k)

    retriever = AutoMergingRetriever(
        base_retriever,
        storage_context=storage_context,
        verbose=True,
    )

    nodes: list[NodeWithScore] = retriever.retrieve(query)

    print(f"[retrieve] Query     : {query!r}")
    print(f"[retrieve] Retrieved : {len(nodes)} context node(s)")
    for i, n in enumerate(nodes, start=1):
        score = f"{n.score:.4f}" if n.score is not None else "N/A"
        print(f"[retrieve]   [{i}] score={score}  chars={len(n.node.get_content())}")
    print()

    return nodes


if __name__ == "__main__":
    from config import SAMPLE_PDF_PATH
    from src.index import build_index
    from src.ingest import load_pdf

    MOCK_QUERY = (
        "Does the data use agreement require informing data subjects about "
        "cross-jurisdictional sharing and the applicable legal frameworks?"
    )

    print("[retrieve] Running standalone Phase 3 test...\n")
    pages = load_pdf(SAMPLE_PDF_PATH)
    index, storage_context = build_index(pages)
    nodes = retrieve_context(MOCK_QUERY, index, storage_context)

    print("=" * 62)
    print("RETRIEVED CONTEXT BLOCKS")
    print("=" * 62)
    for i, n in enumerate(nodes, start=1):
        content = n.node.get_content()
        score = f"{n.score:.4f}" if n.score is not None else "N/A"
        print(f"\n── Node {i} " + "─" * 50)
        print(f"  node_id : {n.node.node_id}")
        print(f"  score   : {score}")
        print(f"  chars   : {len(content)}")
        print(f"  preview :")
        for line in content[:350].splitlines():
            print(f"    {line}")
        if len(content) > 350:
            print("    [... truncated ...]")

    print("\n" + "=" * 62)
    print(f"Phase 3 complete ✓  ({len(nodes)} parent node(s) returned)")
    print("=" * 62)
