# shuscribe/utils.py

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