"""
src/generate.py  -  Phase 4: Guardrailed Generation
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llama_index.core.schema import NodeWithScore
from llama_index.llms.ollama import Ollama

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_REQUEST_TIMEOUT

SYSTEM_PROMPT = """\
You are a compliance analysis assistant for genomic data governance.

You will be given CONTEXT blocks extracted from GA4GH policy documents and a USER QUERY.

Your task is to analyse the context and produce a compliance finding.

RULES:
- Output ONLY a single valid JSON object. No preamble, no explanation, no markdown.
- Do not wrap the JSON in code fences.
- Every field is required. Do not omit any field.
- "severity" must be exactly one of: low, medium, high
- "exact_quote" must be a verbatim substring copied directly from the CONTEXT. Do not paraphrase.

JSON schema:
{
    "finding":      "<concise description of the compliance finding>",
    "severity":     "<low | medium | high>",
    "cited_clause": "<the policy section or clause title being cited>",
    "exact_quote":  "<verbatim substring from the context blocks above>"
}"""


def generate_finding(query: str, context_nodes: list[NodeWithScore]) -> str:
    """
    Generate a guardrailed JSON compliance finding via local Ollama.

    Formats retrieved parent node text into a numbered context block,
    composes a strict system prompt, and calls the local Ollama LLM.
    Returns the raw JSON string for validation by Phase 5.
    No external API calls are made.
    """
    context_block = _build_context_block(context_nodes)
    prompt = _build_prompt(query, context_block)

    llm = Ollama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        request_timeout=OLLAMA_REQUEST_TIMEOUT,
    )

    print(f"[generate] Model     : {OLLAMA_MODEL}")
    print(
        f"[generate] Context   : {len(context_nodes)} node(s), {len(context_block)} chars"
    )
    print("[generate] Calling Ollama...")

    response = llm.complete(prompt)
    raw = _strip_markdown_fences(str(response))

    print(f"[generate] Response  : {len(raw)} chars received")
    print(f"[generate] Raw JSON  :\n{raw}\n")

    return raw


def _build_context_block(context_nodes: list[NodeWithScore]) -> str:
    """Concatenate retrieved node texts into a numbered context block."""
    parts = []
    for i, n in enumerate(context_nodes, start=1):
        parts.append(f"[CONTEXT {i}]\n{n.node.get_content().strip()}")
    return "\n\n".join(parts)


def _build_prompt(query: str, context_block: str) -> str:
    """Compose the full prompt with system instruction, context, and query."""
    return f"{SYSTEM_PROMPT}\n\n{context_block}\n\nUSER QUERY: {query}\n\nJSON:"


def _strip_markdown_fences(raw: str) -> str:
    """Remove accidental ```json ... ``` or ``` ... ``` wrappers from LLM output."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()


if __name__ == "__main__":
    from config import SAMPLE_PDF_PATH
    from src.index import build_index
    from src.ingest import load_pdf
    from src.retrieve import retrieve_context

    MOCK_QUERY = (
        "Does the data use agreement require informing data subjects about "
        "cross-jurisdictional sharing and the applicable legal frameworks?"
    )

    print("[generate] Running standalone Phase 4 test...\n")
    pages = load_pdf(SAMPLE_PDF_PATH)
    index, storage_context = build_index(pages)
    nodes = retrieve_context(MOCK_QUERY, index, storage_context)
    raw_json = generate_finding(MOCK_QUERY, nodes)

    print("=" * 62)
    print("RAW LLM OUTPUT")
    print("=" * 62)
    print(raw_json)
    print("=" * 62)
    print("Phase 4 complete ✓  (pass raw_json to Phase 5 for validation)")
    print("=" * 62)
