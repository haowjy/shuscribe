"""
ProseMirror content utilities for server-side processing
"""
from typing import Dict, Any, List


def compute_word_count_from_prosemirror(content: Dict[str, Any]) -> int:
    """
    Compute word count from ProseMirror JSON content.
    
    Recursively traverses the ProseMirror document tree and sums up
    words from all text nodes. Server-side authoritative count.
    
    Args:
        content: ProseMirror document JSON (should have type="doc")
        
    Returns:
        Total word count (0 for malformed/empty content)
    """
    if not content or not isinstance(content, dict):
        return 0
    
    return _count_words_recursive(content)


def _count_words_recursive(node: Dict[str, Any]) -> int:
    """
    Recursively count words in a ProseMirror node and its children.
    
    Args:
        node: ProseMirror node (dict with type, text, content, etc.)
        
    Returns:
        Word count for this node and all descendants
    """
    if not isinstance(node, dict):
        return 0
    
    word_count = 0
    
    # If this is a text node, count its words
    if node.get("type") == "text" and "text" in node:
        text = node["text"]
        if isinstance(text, str):
            # Split on whitespace and count non-empty words
            words = [word.strip() for word in text.split() if word.strip()]
            word_count += len(words)
    
    # Recursively process children in the "content" array
    content = node.get("content", [])
    if isinstance(content, list):
        for child in content:
            word_count += _count_words_recursive(child)
    
    return word_count
