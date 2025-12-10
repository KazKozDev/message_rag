"""Claude LLM client implementation."""

import os
from typing import Any

from anthropic import Anthropic

from .base import BaseLLMClient


class ClaudeClient(BaseLLMClient):
    """Claude API client implementation."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize Claude client.

        Args:
            config: Configuration dictionary containing model parameters.
        """
        super().__init__(config)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)

    def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate completion for a prompt.

        Args:
            prompt: The input prompt text.
            **kwargs: Additional parameters (system, temperature, max_tokens).

        Returns:
            Generated text completion.
        """
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        system = kwargs.get("system")

        message_params: dict[str, Any] = {
            "model": self.model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system:
            message_params["system"] = system

        response = self.client.messages.create(**message_params)
        return response.content[0].text

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Generate response for chat conversation.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            **kwargs: Additional parameters (system, temperature, max_tokens).

        Returns:
            Generated response text.
        """
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        system = kwargs.get("system")

        message_params: dict[str, Any] = {
            "model": self.model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        if system:
            message_params["system"] = system

        response = self.client.messages.create(**message_params)
        return response.content[0].text

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using Claude's token counting.

        Args:
            text: The input text.

        Returns:
            Approximate number of tokens (4 chars per token estimate).
        """
        # Anthropic doesn't provide a direct token counting API
        # Using rough estimate: ~4 characters per token
        return len(text) // 4
