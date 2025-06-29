def count_tokens(text: str) -> int:
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