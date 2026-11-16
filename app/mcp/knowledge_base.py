"""Logging-only knowledge-base MCP stub backed by the local BM25 index."""

from pathlib import Path

from langchain_core.documents import Document

from app.mcp.common import log_stub_call
from app.policies import build_retriever, search_policies

_retriever = None


def initialize(policies_dir: Path | None = None):
    """Build the in-memory BM25 index at agent startup.

    Called once by `initialize_agent` before the first ticket is processed. In
    production this boundary attaches to a managed knowledge-base/indexing
    service that loads approved, versioned policy documents and exposes a
    searchable MCP resource. It must return an index handle plus document
    version metadata, or fail startup if the approved corpus is unavailable.
    """
    global _retriever
    _retriever = build_retriever(policies_dir) if policies_dir else build_retriever()
    log_stub_call("knowledge_base.initialize", documents=len(_retriever.docs))
    return _retriever


def search_knowledge_base(query: str, top_k: int = 5) -> list[Document]:
    """Retrieve grounded policy chunks for a ticket.

    Called by the `retrieve_policies` graph node after safety routing allows a
    normal FAQ request. In production this should call the broker's approved
    knowledge-base/search MCP server, enforce document access controls, return
    relevance scores and immutable source/page/version metadata, and never
    silently return unapproved content.
    """
    global _retriever
    if _retriever is None:
        initialize()
    _retriever.k = top_k
    results = search_policies(_retriever, query)
    log_stub_call("knowledge_base.search", query=query, top_k=top_k, results=len(results))
    return results
