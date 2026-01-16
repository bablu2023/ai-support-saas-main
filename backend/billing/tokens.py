def estimate_tokens(text: str) -> int:
    """
    Rough but safe token estimate.
    (OpenAI ≈ 4 chars per token)
    """
    if not text:
        return 0
    return max(1, len(text) // 4)
