"""Load and index policy Markdown files with an in-memory BM25 retriever."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DEFAULT_POLICIES_DIR = Path(__file__).parents[1] / "policies" / "md"
PAGE_MARKER = re.compile(r"^## Page (?P<page>\d+)\s*$", re.MULTILINE)
SOURCE_MARKER = re.compile(r"^> Source: (?P<source>.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class PolicyChunk:
    """A chunk returned by BM25 with citation metadata."""

    text: str
    source_files: tuple[str, ...]
    citations: tuple[str, ...]
    score_rank: int


def _policy_name(markdown_path: Path) -> str:
    value = re.sub(r"[_-]+", " ", markdown_path.stem)
    value = re.sub(r"\bvaletax\b", "", value, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", value).strip().title()


def _read_markdown_files(policies_dir: Path) -> str:
    """Concatenate policies with stable source and page markers."""
    markdown_files = sorted(policies_dir.glob("*.md"))
    if not markdown_files:
        raise FileNotFoundError(f"No Markdown policies found in {policies_dir}")
    sections: list[str] = []
    for path in markdown_files:
        content = path.read_text(encoding="utf-8")
        sections.append(
            f"\n\n# Policy: {_policy_name(path)}\n"
            f"<!-- source_file: {path.name} -->\n{content.strip()}"
        )
    return "\n".join(sections)


def _load_page_documents(policies_dir: Path) -> list[Document]:
    """Load source files into page documents before chunking.

    Keeping metadata on the LangChain Document means chunking cannot separate
    a source marker from its text and lose citation information.
    """
    markdown_files = sorted(policies_dir.glob("*.md"))
    page_documents: list[Document] = []
    for path in markdown_files:
        content = path.read_text(encoding="utf-8")
        matches = list(PAGE_MARKER.finditer(content))
        if not matches:
            matches = [re.search(r"^# .+$", content, flags=re.MULTILINE)]
        for index, match in enumerate(matches):
            if match is None:
                continue
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
            page_number = int(match.group("page")) if match.groupdict().get("page") else 1
            page_documents.append(Document(
                page_content=content[start:end].strip(),
                metadata={
                    "source_files": [path.name],
                    "policy_names": [_policy_name(path)],
                    "pages": [page_number],
                    "citations": [f"{_policy_name(path)}, page {page_number}"],
                },
            ))
    return page_documents


def _metadata_for_chunk(chunk: str) -> dict[str, object]:
    """Extract source and page metadata from a concatenated chunk."""
    sources = tuple(dict.fromkeys(SOURCE_MARKER.findall(chunk)))
    pages = tuple(dict.fromkeys(int(value) for value in PAGE_MARKER.findall(chunk)))
    policy_names = tuple(dict.fromkeys(re.findall(
        r"^# Policy: (.+?)\s*$", chunk, flags=re.MULTILINE
    )))
    citations = tuple(
        f"{name}, page {page}" for name in policy_names for page in pages
    )
    return {
        "source_files": list(sources),
        "pages": list(pages),
        "policy_names": list(policy_names),
        "citations": list(citations),
    }


def load_policy_documents(
    policies_dir: Path = DEFAULT_POLICIES_DIR,
    *,
    chunk_size: int = 1200,
    chunk_overlap: int = 150,
) -> list[Document]:
    """Load, concatenate, and split all policies into LangChain Documents."""
    if not list(policies_dir.glob("*.md")):
        raise FileNotFoundError(f"No Markdown policies found in {policies_dir}")
    page_documents = _load_page_documents(policies_dir)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## Page ", "\n\n", "\n", " ", ""],
    )
    documents = splitter.split_documents(page_documents)
    if not documents:
        raise ValueError(f"No text chunks could be created from {policies_dir}")
    return documents


def build_retriever(
    policies_dir: Path = DEFAULT_POLICIES_DIR,
    *,
    k: int = 5,
    chunk_size: int = 1200,
    chunk_overlap: int = 150,
) -> BM25Retriever:
    """Build a BM25 index in memory; call once when the agent starts."""
    documents = load_policy_documents(
        policies_dir, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return BM25Retriever.from_documents(documents, k=k)


def search_policies(retriever: BM25Retriever, query: str) -> list[Document]:
    """Run a BM25 query against the startup-loaded policy index."""
    return retriever.invoke(query)
