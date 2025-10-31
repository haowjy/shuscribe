"""
Utilities for Markdown content: deriving indexable markdown and counting words.

TODO(@md_indexing.py)
- Canonical content policy
  - Document.content must be plain Markdown (canonical source of truth)
  - All other input formats (docx/pdf/html/etc.) must be converted to Markdown
    prior to persistence; do not store HTML/JSON bodies in DB content
  - Optionally store the original file in object storage; compute and persist
    index_markdown and last_indexed_at alongside Markdown content
- Enhance derive_index_markdown()
  - Normalize/strip HTML tags to plain text when present
  - Optionally drop frontmatter blocks (---) or convert to metadata
  - Remove or normalize code fences and inline code; collapse whitespace
  - Replace images with alt text, collect references separately
  - Normalize links: keep link text, collect link targets (http, mailto)
  - Parse wikilinks ([[Title]] / [[Title|alias]]) for graph building
  - Extract headings and ids to support TOC and outline features
- Improve count_words()
  - Ignore code blocks, HTML tags, URLs; use Unicode-aware tokenization
  - Provide approximate token counting for model budgeting
- Index outputs & metadata
  - Return structured index artifacts (index_markdown, preview, hash, language)
  - Add hooks for stemming/stopwords per language
- File upload pipeline (future)
  - Convert docx/pdf/html to Markdown prior to persistence (frontend or worker)
  - Store original in object storage; persist Markdown body as source of truth
  - Compute index_markdown + last_indexed_at on create/update
- Background indexing
  - Debounced async job to refresh index_markdown on content changes
  - Emit events/metrics for indexing status and duration
- Safety & performance
  - Sanitize HTML; cap input size; streaming processing for large files
- Tests
  - Golden tests for tricky Markdown (tables, blockquotes, lists, fences)
  - Property tests to ensure idempotent normalization
"""
from typing import Optional, Iterable
import re

# Optional Mistune support (fast, extensible Markdown parser)
_MISTUNE_AVAILABLE = False
_create_markdown = None
_AstRenderer = None
_MISTUNE_MD = None  # cached parser instance
try:  # Best-effort import across mistune versions
    from mistune import create_markdown as _create_markdown  # type: ignore
    try:
        from mistune.renderers import AstRenderer as _AstRenderer  # type: ignore
    except Exception:  # Older/newer variants
        from mistune import AstRenderer as _AstRenderer  # type: ignore
    _MISTUNE_AVAILABLE = _create_markdown is not None and _AstRenderer is not None
except Exception:
    _MISTUNE_AVAILABLE = False


def derive_index_markdown(md: Optional[str]) -> str:
    """Derive indexable markdown from Markdown. Placeholder: passthrough."""
    return md or ""


def _iter_text_from_ast(nodes: Iterable[dict]) -> Iterable[str]:
    """Yield text from Mistune AST, skipping code/HTML nodes."""
    for node in nodes or []:
        node_type = node.get("type")
        if node_type in {"code", "codespan", "html", "inline_html"}:
            continue
        if node_type == "text":
            text = node.get("text")
            if isinstance(text, str) and text:
                yield text
        # Recurse into children when present
        children = node.get("children")
        if isinstance(children, list) and children:
            yield from _iter_text_from_ast(children)


def _get_mistune_parser():
    global _MISTUNE_MD
    if _MISTUNE_MD is None:
        _MISTUNE_MD = _create_markdown(renderer=_AstRenderer())  # type: ignore
    return _MISTUNE_MD


def _count_words_with_mistune(md: str) -> int:
    parser = _get_mistune_parser()
    ast = parser(md)
    words = 0
    for chunk in _iter_text_from_ast(ast if isinstance(ast, list) else []):
        words += len(chunk.split())
    return words


def _count_words_naive(md: str) -> int:
    # Remove heading markers at line starts like '#', '##', etc.
    text = re.sub(r"(^|\n)\s*#+\s*", r"\1", md)
    # Remove unordered list markers at line starts: '-', '*', '+' followed by space
    text = re.sub(r"(^|\n)\s*[-*+]\s+", r"\1", text)
    return len(text.split())


def count_words(md: Optional[str]) -> int:
    """Count words in Markdown content.

    Prefers Mistune AST-based parsing when available (skips code/HTML); falls
    back to a simple token-based approximation otherwise.
    """
    if not md:
        return 0
    try:
        if _MISTUNE_AVAILABLE:
            return _count_words_with_mistune(md)
    except Exception:
        # Fall back to naive counting on any parsing error
        pass
    return _count_words_naive(md)



