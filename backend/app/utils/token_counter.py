def estimate_tokens(text: str) -> int:
    """Rough estimate of tokens (average ~4 characters per token in English)."""
    if not text:
        return 0
    return max(1, len(text) // 4)
