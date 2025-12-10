"""Tests for token counter."""

from src.utils.token_counter import TokenCounter


def test_token_counter_initialization() -> None:
    """Test token counter initialization."""
    counter = TokenCounter()
    assert counter.model == "gpt-3.5-turbo"
    assert counter.chars_per_token == 4


def test_count_empty_string() -> None:
    """Test counting tokens in empty string."""
    counter = TokenCounter()
    assert counter.count("") == 0


def test_count_simple_text() -> None:
    """Test counting tokens in simple text."""
    counter = TokenCounter()
    text = "Hello world"
    count = counter.count(text)
    # ~11 chars / 4 = ~2-3 tokens
    assert count >= 2
    assert count <= 3


def test_count_longer_text() -> None:
    """Test counting tokens in longer text."""
    counter = TokenCounter()
    text = "This is a longer piece of text that should have more tokens."
    count = counter.count(text)
    # ~62 chars / 4 = ~15 tokens
    assert count >= 10
    assert count <= 20


def test_truncate_short_text() -> None:
    """Test truncating text that's already under limit."""
    counter = TokenCounter()
    text = "Short text"
    truncated = counter.truncate(text, max_tokens=10)
    assert truncated == text


def test_truncate_long_text() -> None:
    """Test truncating text that exceeds limit."""
    counter = TokenCounter()
    text = "A" * 100
    truncated = counter.truncate(text, max_tokens=10)
    # 10 tokens * 4 chars = 40 chars
    assert len(truncated) == 40


def test_truncate_empty_string() -> None:
    """Test truncating empty string."""
    counter = TokenCounter()
    assert counter.truncate("", max_tokens=10) == ""


def test_split_by_tokens_empty() -> None:
    """Test splitting empty string."""
    counter = TokenCounter()
    chunks = counter.split_by_tokens("", chunk_size=10)
    assert chunks == []


def test_split_by_tokens_single_chunk() -> None:
    """Test splitting text that fits in single chunk."""
    counter = TokenCounter()
    text = "Short text"
    chunks = counter.split_by_tokens(text, chunk_size=10)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_split_by_tokens_multiple_chunks() -> None:
    """Test splitting text into multiple chunks."""
    counter = TokenCounter()
    text = "A" * 100
    chunks = counter.split_by_tokens(text, chunk_size=10)
    # 100 chars / (10 tokens * 4 chars) = 100 / 40 = 3 chunks
    assert len(chunks) == 3
    assert sum(len(chunk) for chunk in chunks) == 100
