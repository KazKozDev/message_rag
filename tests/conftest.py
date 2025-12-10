"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def temp_dir() -> Path:
    """Create temporary directory for tests.

    Returns:
        Path to temporary directory.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_message() -> dict[str, Any]:
    """Sample message for testing.

    Returns:
        Message dictionary.
    """
    return {
        "message_id": "test_001",
        "url": "https://example.com/test_001",
        "author": "Test User",
        "timestamp": "2025-01-01T00:00:00Z",
        "content": "This is a test message",
        "metadata": {"channel": "test", "tags": ["test"]},
    }


@pytest.fixture
def sample_messages() -> list[dict[str, Any]]:
    """Sample messages for testing.

    Returns:
        List of message dictionaries.
    """
    return [
        {
            "message_id": "msg_001",
            "url": "https://example.com/msg_001",
            "author": "Alice",
            "timestamp": "2025-01-01T10:00:00Z",
            "content": "We need to discuss the budget allocation for Q2.",
            "metadata": {"channel": "planning", "tags": ["budget"]},
        },
        {
            "message_id": "msg_002",
            "url": "https://example.com/msg_002",
            "author": "Bob",
            "timestamp": "2025-01-01T11:00:00Z",
            "content": "The new feature is ready for testing.",
            "metadata": {"channel": "engineering", "tags": ["feature"]},
        },
        {
            "message_id": "msg_003",
            "url": "https://example.com/msg_003",
            "author": "Charlie",
            "timestamp": "2025-01-01T12:00:00Z",
            "content": "User feedback shows positive response to the redesign.",
            "metadata": {"channel": "product", "tags": ["feedback"]},
        },
    ]
