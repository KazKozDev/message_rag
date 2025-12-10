"""Tests for response cache."""

import time
from pathlib import Path

from src.utils.cache import ResponseCache


def test_cache_initialization(temp_dir: Path) -> None:
    """Test cache initialization."""
    cache = ResponseCache(cache_dir=str(temp_dir), ttl_seconds=3600)
    assert cache.cache_dir == temp_dir
    assert cache.ttl_seconds == 3600
    assert cache.cache_dir.exists()


def test_cache_set_and_get(temp_dir: Path) -> None:
    """Test setting and getting cached responses."""
    cache = ResponseCache(cache_dir=str(temp_dir), ttl_seconds=3600)

    prompt = "What is AI?"
    model = "claude"
    response = "AI is artificial intelligence."

    cache.set(prompt, model, response)
    retrieved = cache.get(prompt, model)

    assert retrieved == response


def test_cache_miss(temp_dir: Path) -> None:
    """Test cache miss returns None."""
    cache = ResponseCache(cache_dir=str(temp_dir), ttl_seconds=3600)

    result = cache.get("nonexistent prompt", "claude")
    assert result is None


def test_cache_expiration(temp_dir: Path) -> None:
    """Test cache entries expire after TTL."""
    cache = ResponseCache(cache_dir=str(temp_dir), ttl_seconds=1)

    prompt = "What is AI?"
    model = "claude"
    response = "AI is artificial intelligence."

    cache.set(prompt, model, response)

    # Should be available immediately
    assert cache.get(prompt, model) == response

    # Wait for expiration
    time.sleep(1.5)

    # Should be expired
    assert cache.get(prompt, model) is None


def test_cache_different_models(temp_dir: Path) -> None:
    """Test cache distinguishes between different models."""
    cache = ResponseCache(cache_dir=str(temp_dir), ttl_seconds=3600)

    prompt = "What is AI?"
    response1 = "Claude response"
    response2 = "GPT response"

    cache.set(prompt, "claude", response1)
    cache.set(prompt, "gpt", response2)

    assert cache.get(prompt, "claude") == response1
    assert cache.get(prompt, "gpt") == response2


def test_cache_clear(temp_dir: Path) -> None:
    """Test clearing cache."""
    cache = ResponseCache(cache_dir=str(temp_dir), ttl_seconds=3600)

    cache.set("prompt1", "claude", "response1")
    cache.set("prompt2", "claude", "response2")

    count = cache.clear()
    assert count == 2

    assert cache.get("prompt1", "claude") is None
    assert cache.get("prompt2", "claude") is None


def test_cache_overwrite(temp_dir: Path) -> None:
    """Test overwriting existing cache entry."""
    cache = ResponseCache(cache_dir=str(temp_dir), ttl_seconds=3600)

    prompt = "What is AI?"
    model = "claude"

    cache.set(prompt, model, "First response")
    cache.set(prompt, model, "Second response")

    assert cache.get(prompt, model) == "Second response"


def test_cache_clear_expired(temp_dir: Path) -> None:
    """Test clearing only expired entries."""
    cache = ResponseCache(cache_dir=str(temp_dir), ttl_seconds=1)

    # Add two entries
    cache.set("prompt1", "claude", "response1")
    time.sleep(0.5)
    cache.set("prompt2", "claude", "response2")

    # Wait for first to expire
    time.sleep(0.7)

    count = cache.clear_expired()

    # First should be expired, second should remain
    assert count >= 1
    assert cache.get("prompt1", "claude") is None
    assert cache.get("prompt2", "claude") == "response2"
