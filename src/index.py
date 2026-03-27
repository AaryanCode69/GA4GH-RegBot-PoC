"""
src/index.py  -  Phase 2: Hierarchical Chunking & Indexing
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import chromadb
from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from config import (
    CHILD_CHUNK_SIZE,
    CHROMA_COLLECTION_NAME,
    CHROMA_DIR,
    CHUNK_OVERLAP,
    EMBED_MODEL_NAME,
    PARENT_CHUNK_SIZE,
    SAMPLE_PDF_PATH,
)


def build_index(pages: list[dict[str, Any]]) -> tuple[VectorStoreIndex, StorageContext]:
    """
    Build a hierarchical vector index from Phase 1 page dicts.

    Converts pages → LlamaIndex Documents → HierarchicalNodeParser →
    parent nodes (1024 tokens) + child nodes (256 tokens).
    Only child nodes are embedded and stored in ChromaDB.
    All nodes (parent + child) go into SimpleDocumentStore so Phase 3's
    AutoMergingRetriever can expand child hits to their parent context.

    Returns (VectorStoreIndex, StorageContext).
    """
    # Convert page dicts to LlamaIndex Documents
    documents = [
        Document(
            text=page["text"],
            metadata={
                "page_number": page["page_number"],
                "source_file": page["source_file"],
                "source_path": page["source_path"],
            },
        )
        for page in pages
    ]
    print(f"[index] {len(documents)} document(s) prepared")

    # Parse into parent/child node hierarchy
    parser = HierarchicalNodeParser.from_defaults(
        chunk_sizes=[PARENT_CHUNK_SIZE, CHILD_CHUNK_SIZE],
        chunk_overlap=CHUNK_OVERLAP,
    )
    all_nodes = parser.get_nodes_from_documents(documents)
    leaf_nodes = get_leaf_nodes(all_nodes)
    parent_count = len(all_nodes) - len(leaf_nodes)

    print(
        f"[index] Nodes: {len(all_nodes)} total  ({parent_count} parent, {len(leaf_nodes)} child)"
    )

    # Local embedding model — zero external API calls
    embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
    print(f"[index] Embedding model: {EMBED_MODEL_NAME}")

    # Reset ChromaDB collection on each run to avoid stale/duplicate vectors
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        chroma_client.delete_collection(CHROMA_COLLECTION_NAME)
    except Exception:
        pass
    chroma_collection = chroma_client.create_collection(CHROMA_COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    print(f"[index] ChromaDB collection '{CHROMA_COLLECTION_NAME}' ready")

    # SimpleDocumentStore holds ALL nodes (parent + child).
    # AutoMergingRetriever in Phase 3 looks up parents by ID from this store.
    docstore = SimpleDocumentStore()
    docstore.add_documents(all_nodes)

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        docstore=docstore,
    )

    # Embed and persist child (leaf) nodes only
    print(f"[index] Embedding {len(leaf_nodes)} child nodes into ChromaDB...")
    index = VectorStoreIndex(
        leaf_nodes,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )

    print(f"[index] ChromaDB: {chroma_collection.count()} vectors stored")
    print("[index] Phase 2 complete ✓\n")

    return index, storage_context


if __name__ == "__main__":
    from src.ingest import load_pdf

    pages = load_pdf(SAMPLE_PDF_PATH)
    index, storage_context = build_index(pages)
    print(f"[index] Docstore node count: {len(storage_context.docstore.docs)}")
    print("[index] Index ready for Phase 3.")
