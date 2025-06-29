"""
JSON Cleaning Utilities

Utilities for extracting and cleaning JSON from LLM responses that may contain
markdown code blocks, extra text, or other formatting artifacts.
"""

import re
import json
from typing import Optional, Union, Dict, Any
import logging

logger = logging.getLogger(__name__)


def clean_json_from_llm_response(response: str) -> str:
    """
    Extract clean JSON from an LLM response that may contain markdown code blocks or extra text.
    
    This function handles several common LLM response patterns:
    1. JSON wrapped in ```json ``` markdown code blocks (gets outermost blocks)
    2. JSON with nested backticks inside the content
    3. Raw JSON mixed with other text (finds first complete JSON object)
    4. Multiple JSON blocks (returns the first valid one)
    
    Args:
        response: Raw LLM response string that may contain JSON
        
    Returns:
        Clean JSON string ready for parsing
        
    Raises:
        ValueError: If no valid JSON could be extracted from the response
        
    Examples:
        >>> clean_json_from_llm_response('```json\\n{"key": "value"}\\n```')
        '{"key": "value"}'
        
        >>> clean_json_from_llm_response('Here is the result: {"key": "value"} Done!')
        '{"key": "value"}'
        
        >>> clean_json_from_llm_response('```json\\n{"inner": "```txt\\ncode\\n```"}\\n```')
        '{"inner": "```txt\\ncode\\n```"}'
    """
    if not response or not response.strip():
        raise ValueError("Empty response provided")
    
    response = response.strip()
    
    # Strategy 1: Look for ```json ``` markdown code blocks
    json_from_markdown = _extract_json_from_markdown(response)
    if json_from_markdown:
        return json_from_markdown
    
    # Strategy 2: Look for any ``` code blocks (might be unlabeled JSON)
    json_from_code_block = _extract_json_from_code_block(response)
    if json_from_code_block:
        return json_from_code_block
    
    # Strategy 3: Look for raw JSON objects in the text
    json_from_raw = _extract_raw_json(response)
    if json_from_raw:
        return json_from_raw
    
    # If all strategies fail, raise an error
    raise ValueError(f"Could not extract valid JSON from response. Response preview: {response[:200]}...")


def _extract_json_from_markdown(response: str) -> Optional[str]:
    """Extract JSON from ```json ``` markdown code blocks, handling nested backticks."""
    # Pattern to match ```json at the start of a line, followed by content, then closing ```
    # Use non-greedy matching and ensure we get the outermost blocks
    pattern = r'```json\s*\n(.*?)\n```'
    
    matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        json_candidate = match.strip()
        if _is_valid_json(json_candidate):
            logger.debug("✅ Extracted JSON from ```json``` markdown block")
            return json_candidate
    
    return None


def _extract_json_from_code_block(response: str) -> Optional[str]:
    """Extract JSON from generic ``` code blocks that might contain JSON."""
    # Pattern to match any ``` code block
    pattern = r'```[a-zA-Z]*\s*\n(.*?)\n```'
    
    matches = re.findall(pattern, response, re.DOTALL)
    
    for match in matches:
        json_candidate = match.strip()
        if _is_valid_json(json_candidate):
            logger.debug("✅ Extracted JSON from generic code block")
            return json_candidate
    
    return None


def _extract_raw_json(response: str) -> Optional[str]:
    """Extract raw JSON objects from text, finding the first complete { } pair."""
    # Find all potential JSON objects by looking for { } pairs
    brace_count = 0
    start_pos = None
    
    for i, char in enumerate(response):
        if char == '{':
            if brace_count == 0:
                start_pos = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_pos is not None:
                # Found a complete JSON object
                json_candidate = response[start_pos:i+1]
                if _is_valid_json(json_candidate):
                    logger.debug("✅ Extracted JSON from raw text")
                    return json_candidate
                # Reset for next potential JSON object
                start_pos = None
    
    return None


def _is_valid_json(text: str) -> bool:
    """Check if a string is valid JSON without raising exceptions."""
    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def parse_cleaned_json(response: str) -> Union[Dict[Any, Any], list]:
    """
    Clean and parse JSON from an LLM response in one step.
    
    Args:
        response: Raw LLM response string
        
    Returns:
        Parsed JSON object (dict or list)
        
    Raises:
        ValueError: If JSON could not be extracted or parsed
        json.JSONDecodeError: If the extracted JSON is malformed
    """
    cleaned_json = clean_json_from_llm_response(response)
    return json.loads(cleaned_json)


# Example usage and test cases
if __name__ == "__main__":
    # Test cases
    test_cases = [
        # Basic markdown JSON
        '```json\n{"key": "value"}\n```',
        
        # JSON with nested backticks
        '```json\n{"inner": "```txt\\ncode\\n```", "other": "value"}\n```',
        
        # Raw JSON with extra text
        'Here is the result: {"key": "value"} Done!',
        
        # Multiple JSON objects (should return first valid one)
        '{"first": "json"} and also {"second": "json"}',
        
        # JSON in generic code block
        '```\n{"unlabeled": "json"}\n```',
        
        # Complex nested case
        '''```json
        {
            "story_prediction": "This story appears to be heading toward...",
            "code_example": "```python\\nprint('hello')\\n```",
            "other_field": "value"
        }
        ```''',
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            result = clean_json_from_llm_response(test_case)
            parsed = json.loads(result)
            print(f"✅ Test {i}: Success - {len(result)} chars extracted")
        except Exception as e:
            print(f"❌ Test {i}: Failed - {e}") 