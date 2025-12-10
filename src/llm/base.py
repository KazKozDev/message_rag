"""Base LLM client interface."""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize LLM client with configuration.

        Args:
            config: Configuration dictionary containing model parameters.
        """
        self.config = config
        self.model_name = config.get("model_name")
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = config.get("temperature", 0.7)

    @abstractmethod
    def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate completion for a prompt.

        Args:
            prompt: The input prompt text.
            **kwargs: Additional model-specific parameters.

        Returns:
            Generated text completion.
        """
        pass

    @abstractmethod
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Generate response for chat conversation.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            **kwargs: Additional model-specific parameters.

        Returns:
            Generated response text.
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: The input text.

        Returns:
            Number of tokens.
        """
        pass
