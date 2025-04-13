# shuscribe/utils.py

from typing import TypeVar
from pydantic import BaseModel

def find_last_json_block(text: str) -> str | None:
    # Find the last occurrence of ```json
    last_json_start = text.rfind("```json")
    
    if last_json_start == -1:
        return None  # No JSON block found
    
    # Find the closing ``` that comes after our opening ```json
    remaining_text = text[last_json_start + 7:]  # Skip past "```json"
    
    # Look for the next closing ```
    closing_pos = remaining_text.find("```")
    
    if closing_pos == -1:
        return None  # No closing backticks found
    
    # Extract the JSON content (without the backticks)
    json_content = remaining_text[:closing_pos].strip()
    
    return json_content

def simple_token_estimator(text: str) -> int:
    """Simple token estimator that estimates the number of tokens based on:
    
    1 token ~= 4 chars in English
    1 token ~= 3/4 words
    
    and taking the average of the two.

    Args:
        text (str): The text to estimate the number of tokens in.

    Returns:
        int: The estimated number of tokens in the text.
    """
    word_count = len(text.split(" "))
    char_count = len(text)
    tokens_count_word_est = word_count / 0.75
    tokens_count_char_est = char_count / 4.0
    return int((tokens_count_word_est + tokens_count_char_est) / 2)




T = TypeVar("T", bound=BaseModel)


def merge_pydantic_models(base: T, nxt: T) -> T:
    """Merge two Pydantic model instances.

    The attributes of 'base' and 'nxt' that weren't explicitly set are dumped into dicts
    using '.model_dump(exclude_unset=True)', which are then merged using 'deepmerge',
    and the merged result is turned into a model instance using '.model_validate'.

    For attributes set on both 'base' and 'nxt', the value from 'nxt' will be used in
    the output result.
    """
    base_dict = base.model_dump(exclude_unset=True)
    nxt_dict = nxt.model_dump(exclude_unset=True)
    merged_dict = base_dict | nxt_dict
    return base.model_validate(merged_dict)