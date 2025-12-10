"""RAG query engine for answering questions with source attribution."""

from typing import Any

import yaml

from ..llm.base import BaseLLMClient
from ..utils.logger import get_logger
from .vector_store import VectorStore

logger = get_logger(__name__)


class QueryEngine:
    """RAG query engine for answering questions based on message history."""

    def __init__(
        self,
        llm_client: BaseLLMClient,
        vector_store: VectorStore,
        prompts_config_path: str = "config/prompts.yaml",
        top_k: int = 3,
        min_similarity: float = 0.7,
    ) -> None:
        """Initialize query engine.

        Args:
            llm_client: LLM client for generating answers.
            vector_store: Vector store for retrieving relevant messages.
            prompts_config_path: Path to prompts configuration file.
            top_k: Number of top results to retrieve.
            min_similarity: Minimum similarity score for results.
        """
        self.llm_client = llm_client
        self.vector_store = vector_store
        self.top_k = top_k
        self.min_similarity = min_similarity

        # Load prompts
        with open(prompts_config_path) as f:
            prompts_config = yaml.safe_load(f)

        self.system_prompt = prompts_config["system_prompts"]["rag_answerer"]
        self.query_template = prompts_config["templates"]["rag_query"]

        logger.info("Initialized query engine")

    def _format_context(self, results: list[dict[str, Any]]) -> str:
        """Format retrieved messages into context string.

        Args:
            results: List of retrieved message results.

        Returns:
            Formatted context string.
        """
        context_parts = []

        for i, result in enumerate(results, 1):
            content = result["content"]
            metadata = result["metadata"]
            url = metadata.get("url", "")
            author = metadata.get("author", "Unknown")
            timestamp = metadata.get("timestamp", "")

            context_part = f"""Message {i}:
Author: {author}
Timestamp: {timestamp}
URL: {url}
Content: {content}
"""
            context_parts.append(context_part)

        return "\n".join(context_parts)

    def query(self, question: str) -> dict[str, Any]:
        """Answer a question based on message history.

        Args:
            question: User's question.

        Returns:
            Dictionary containing answer, sources, and metadata.
        """
        logger.info(f"Processing query: {question}")

        # Retrieve relevant messages
        results = self.vector_store.search(
            query=question,
            top_k=self.top_k,
            min_similarity=self.min_similarity,
        )

        if not results:
            logger.warning("No relevant messages found for query")
            return {
                "answer": "I couldn't find any relevant messages to answer your question.",
                "sources": [],
                "context_used": [],
            }

        # Format context
        context = self._format_context(results)

        # Build prompt
        prompt = self.query_template.format(context=context, question=question)

        # Generate answer
        logger.debug("Generating answer with LLM")
        answer = self.llm_client.complete(prompt, system=self.system_prompt)

        # Build sources list
        sources = []
        for result in results:
            metadata = result["metadata"]
            source = {
                "url": metadata.get("url", ""),
                "author": metadata.get("author", "Unknown"),
                "timestamp": metadata.get("timestamp", ""),
                "score": result["score"],
                "content_preview": (
                    result["content"][:100] + "..."
                    if len(result["content"]) > 100
                    else result["content"]
                ),
            }
            sources.append(source)

        response = {
            "answer": answer,
            "sources": sources,
            "context_used": results,
            "num_sources": len(sources),
        }

        logger.info(f"Query completed with {len(sources)} sources")
        return response

    def format_response(self, response: dict[str, Any]) -> str:
        """Format query response for display.

        Args:
            response: Response dictionary from query method.

        Returns:
            Formatted response string.
        """
        output = response["answer"]

        if not response["sources"]:
            return output

        # Add sources section if not already in answer
        if "Sources:" not in output:
            output += "\n\nSources:\n"
            for source in response["sources"]:
                url = source["url"]
                author = source["author"]
                preview = source["content_preview"]
                output += f"- {preview} by {author} ({url})\n"

        return output
