# GA4GH-RegBot — Proof of Concept

A **local-first** Retrieval-Augmented Generation (RAG) pipeline that ingests GA4GH policy documents, retrieves hierarchical legal context, and produces citation-grounded compliance findings with deterministic validation.

Built as a Proof of Concept for **Google Summer of Code 2025** to validate the core technical assumptions of the GA4GH-RegBot proposal before the full MVP implementation.

---

## What This PoC Validates

| Assumption | How it is tested |
|---|---|
| Local-only pipeline is viable | Zero calls to OpenAI, Anthropic, or any external embedding API |
| Hierarchical chunking improves legal context retrieval | `HierarchicalNodeParser` (parent 1024 tok / child 256 tok) + `AutoMergingRetriever` |
| LLM output can be schema-constrained reliably | Strict system prompt enforcing JSON-only output with 4 required fields |
| Citations cannot be hallucinated | `exact_quote` verified as a verbatim substring of retrieved source text in Phase 5 |

---

## Pipeline

```
Input Query
    │
    │   data/pdfs/
    │       │
    ▼       ▼
Phase 1 ── PyMuPDF extraction ──────────────────── List[dict]
               page text + metadata (page_number, source_file)
    │
    ▼
Phase 2 ── HierarchicalNodeParser ──────────────── Parent nodes (1024 tok)
           HuggingFaceEmbedding (local)             Child nodes  (256 tok)
           ChromaDB PersistentClient                      │
                                                    ChromaDB (vectors)
                                                    SimpleDocumentStore (all nodes)
    │
    ▼
Phase 3 ── ChromaDB vector search ──────────────── Top-K child node hits
           AutoMergingRetriever                     expanded → parent context blocks
    │
    ▼
Phase 4 ── Ollama llama3.1:8b (local) ─────────── Raw JSON string
           Guardrailed system prompt
           JSON-only output enforced
    │
    ▼
Phase 5 ── Deterministic validation ────────────── Final dict
           JSON parse check                         validation_passed: bool
           Required fields check                    validation_errors: list
           Severity value check
           exact_quote substring check  ◄── core guarantee
```

---

## Tech Stack

| Component | Library / Model |
|---|---|
| PDF parsing | `PyMuPDF` (`fitz`) |
| RAG orchestration | `llama-index-core` |
| Hierarchical chunking | `HierarchicalNodeParser` + `AutoMergingRetriever` |
| Vector store | `ChromaDB` (local persistent) |
| Embeddings | `BAAI/bge-small-en-v1.5` via `llama-index-embeddings-huggingface` |
| LLM inference | `Ollama` — `llama3.1:8b-instruct-q4_K_M` |
| Validation | Pure Python — `json.loads` + `str.__contains__` |

---

## Prerequisites

Before running anything, ensure all of the following are in place.

**1. Python 3.11**
```bash
python --version   # must show 3.11.x
```

**2. Ollama installed and the daemon running**

Download from https://ollama.com/download, then:
```bash
ollama serve
```

**3. Model pulled**
```bash
ollama pull llama3.1:8b-instruct-q4_K_M
```

---

## Setup

```bash
# 1. Navigate to the PoC directory
cd GA4GH-RegBot/POC

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Generate the sample GA4GH policy PDF
python scripts/create_sample_pdf.py
```

`create_sample_pdf.py` generates `data/pdfs/sample_ga4gh_policy.pdf` — a
realistic 2-page GA4GH-style policy document with 8 numbered sections covering
consent, data access governance, cross-jurisdictional compliance, privacy
obligations, and accountability. This is the corpus the pipeline runs against.

---

## Running

### Full pipeline — all 5 phases in sequence
```bash
python main.py
```

### Individual phases — standalone verification
Each module can be run independently to verify a single phase without
executing the full pipeline.

```bash
python -m src.ingest     # Phase 1: PDF extraction report
python -m src.index      # Phase 2: Build and persist ChromaDB index
python -m src.retrieve   # Phase 3: Small-to-big retrieval report
python -m src.generate   # Phase 4: Guardrailed generation (requires Ollama)
python -m src.validate   # Phase 5: Full pipeline + validation report
```

---

## Expected Output

A successful `python main.py` run prints a phase-by-phase log and ends with
a validated JSON finding:

```
=================================================================
  GA4GH-RegBot PoC – Local-First Compliance Pipeline
=================================================================

[main] ── Phase 1: Ingestion & Parsing ──────────────────────
[ingest] Opened 'sample_ga4gh_policy.pdf'  (2 pages detected)
[ingest]   Page   1:   1893 chars extracted
[ingest]   Page   2:   2021 chars extracted
[main]    2 page(s) ingested successfully.

[main] ── Phase 2: Hierarchical Chunking & Indexing ─────────
[index] 2 document(s) prepared
[index] Nodes: 12 total  (4 parent, 8 child)
[index] Embedding model: BAAI/bge-small-en-v1.5
[index] ChromaDB collection 'ga4gh_policy_chunks' ready
[index] Embedding 8 child nodes into ChromaDB...
[index] ChromaDB: 8 vectors stored
[main]    Index built and persisted to ChromaDB.

[main] ── Phase 3: Small-to-Big Retrieval ───────────────────
[retrieve] Retrieved : 2 context node(s)
[main]    2 parent context node(s) retrieved.

[main] ── Phase 4: Guardrailed Generation ───────────────────
[generate] Model     : llama3.1:8b-instruct-q4_K_M
[generate] Calling Ollama...
[main]    Raw LLM output received.

[main] ── Phase 5: Deterministic Citation Validation ─────────
[validate] validation_passed : True
[validate]   ✓ All checks passed

[main]    Final validated output:

{
  "finding": "The data use agreement must document cross-jurisdictional compliance assessment prior to initiating international data sharing.",
  "severity": "high",
  "cited_clause": "7. Cross-Jurisdictional Compliance",
  "exact_quote": "Institutions must document their cross-jurisdictional compliance assessment prior to initiating any international data sharing activity",
  "validation_passed": true,
  "validation_errors": []
}
```

`validation_passed: true` with an empty `validation_errors` list confirms the
`exact_quote` exists verbatim in the retrieved source text — no hallucinated
citation can pass Phase 5.

---

## File Structure

```
POC/
├── requirements.txt              # All dependencies pinned to exact versions
├── config.py                     # Single source of truth: paths, models, hyperparams
├── main.py                       # Full pipeline orchestrator (all 5 phases)
├── executionplan.md              # Phase-by-phase build tracker
│
├── data/
│   ├── pdfs/
│   │   └── sample_ga4gh_policy.pdf   # Generated by scripts/create_sample_pdf.py
│   └── chroma_db/                    # ChromaDB persistent vector store (auto-created)
│
├── src/
│   ├── __init__.py
│   ├── ingest.py                 # Phase 1: PyMuPDF text extraction
│   ├── index.py                  # Phase 2: Hierarchical chunking + ChromaDB indexing
│   ├── retrieve.py               # Phase 3: Small-to-big retrieval
│   ├── generate.py               # Phase 4: Guardrailed Ollama generation
│   └── validate.py               # Phase 5: Deterministic citation validation
│
└── scripts/
    └── create_sample_pdf.py      # One-time utility: generates sample policy PDF
```

---

## Absolute Constraints

These rules are enforced across every module per `poc-architecture-rules.md`:

- **Zero external APIs** — no document data or queries leave the machine.
  All embedding (`BAAI/bge-small-en-v1.5`) and inference (`Ollama`) run locally.

- **Evidence determinism** — the `exact_quote` field in every finding must be
  a 100% verifiable substring of the retrieved chunk. Phase 5 enforces this
  with a pure Python `in` check. Hallucinated citations produce
  `validation_passed: false`.

- **Modular design** — each phase lives in its own file and is independently
  runnable. No module imports from a later phase.

---

## Configuration

All tunable parameters are centralised in `config.py`. Key values:

| Parameter | Default | Description |
|---|---|---|
| `EMBED_MODEL_NAME` | `BAAI/bge-small-en-v1.5` | Local HuggingFace embedding model |
| `OLLAMA_MODEL` | `llama3.1:8b-instruct-q4_K_M` | Ollama model tag |
| `PARENT_CHUNK_SIZE` | `1024` | Token size for parent nodes |
| `CHILD_CHUNK_SIZE` | `256` | Token size for child nodes |
| `TOP_K_RETRIEVAL` | `3` | Child nodes retrieved before parent expansion |
| `OLLAMA_REQUEST_TIMEOUT` | `120.0` | Seconds before Ollama call times out |

---

## Attribution

Sample policy document content is modelled on GA4GH released documents.
Use and reproduction is subject to the
[GA4GH Copyright Policy](https://www.ga4gh.org/copyright-policy/).
