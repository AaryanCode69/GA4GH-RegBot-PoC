"""
config.py – Central Configuration for GA4GH-RegBot PoC

All paths, model names, chunk sizes, and hyperparameters are defined here.
Every other module imports from this file – no magic strings elsewhere.
"""

from __future__ import annotations

from pathlib import Path

# ── Project Root ──────────────────────────────────────────────────────────────
ROOT_DIR: Path = Path(__file__).parent.resolve()

# ── Data Paths ────────────────────────────────────────────────────────────────
DATA_DIR: Path = ROOT_DIR / "data"
PDF_DIR: Path = DATA_DIR / "pdfs"
CHROMA_DIR: Path = DATA_DIR / "chroma_db"

# Ensure critical directories exist at import time
PDF_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# ── Sample PDF ────────────────────────────────────────────────────────────────
SAMPLE_PDF_PATH: Path = PDF_DIR / "sample_ga4gh_policy.pdf"

# ── Embedding Model (local HuggingFace – no external API calls) ───────────────
EMBED_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"

# ── LLM – Ollama (local inference only) ──────────────────────────────────────
OLLAMA_MODEL: str = "llama3.1:8b-instruct-q4_K_M"
OLLAMA_BASE_URL: str = "http://localhost:11434"
OLLAMA_REQUEST_TIMEOUT: float = 120.0

# ── ChromaDB ──────────────────────────────────────────────────────────────────
CHROMA_COLLECTION_NAME: str = "ga4gh_policy_chunks"

# ── Hierarchical Chunking Sizes (in tokens) ───────────────────────────────────
# Parent nodes  – larger context blocks passed to the LLM for generation
PARENT_CHUNK_SIZE: int = 1024
# Child nodes   – smaller, citation-sized blocks used for vector search
CHILD_CHUNK_SIZE: int = 256
# Overlap between consecutive chunks to preserve cross-boundary context
CHUNK_OVERLAP: int = 20

# ── Retrieval ─────────────────────────────────────────────────────────────────
# Number of child nodes to retrieve from ChromaDB before parent expansion
TOP_K_RETRIEVAL: int = 3

# ── Output JSON Contract ──────────────────────────────────────────────────────
# These are the exact fields the LLM must produce (enforced in validate.py)
REQUIRED_OUTPUT_FIELDS: frozenset[str] = frozenset(
    {"finding", "severity", "cited_clause", "exact_quote"}
)
VALID_SEVERITY_VALUES: frozenset[str] = frozenset({"low", "medium", "high"})
