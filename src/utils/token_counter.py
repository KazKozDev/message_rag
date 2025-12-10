"""Token counting and text manipulation utilities."""


class TokenCounter:
    """Utility for counting and managing tokens."""

    def __init__(self, model: str = "gpt-3.5-turbo") -> None:
        """Initialize token counter.

        Args:
            model: Model name for tokenizer selection.
        """
        self.model = model
        # Simple character-based approximation
        # For production, use tiktoken or similar
        self.chars_per_token = 4

    def count(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: Input text to count tokens.

        Returns:
            Approximate number of tokens.
        """
        if not text:
            return 0
        return len(text) // self.chars_per_token

    def truncate(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit.

        Args:
            text: Input text to truncate.
            max_tokens: Maximum number of tokens allowed.

        Returns:
            Truncated text.
        """
        if not text:
            return ""

        max_chars = max_tokens * self.chars_per_token
        if len(text) <= max_chars:
            return text

        return text[:max_chars]

    def split_by_tokens(self, text: str, chunk_size: int) -> list[str]:
        """Split text into chunks by token count.

        Args:
            text: Input text to split.
            chunk_size: Maximum tokens per chunk.

        Returns:
            List of text chunks.
        """
        if not text:
            return []

        max_chars = chunk_size * self.chars_per_token
        chunks = []

        for i in range(0, len(text), max_chars):
            chunks.append(text[i : i + max_chars])

        return chunks
