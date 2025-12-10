"""Message processing and ingestion."""

import json
from pathlib import Path
from typing import Any

from ..utils.logger import get_logger
from .vector_store import VectorStore

logger = get_logger(__name__)


class MessageProcessor:
    """Process and ingest messages into vector store."""

    def __init__(self, vector_store: VectorStore) -> None:
        """Initialize message processor.

        Args:
            vector_store: Vector store instance for storing embeddings.
        """
        self.vector_store = vector_store

    def load_messages_from_file(self, file_path: str) -> list[dict[str, Any]]:
        """Load messages from JSON file.

        Args:
            file_path: Path to JSON file containing messages.

        Returns:
            List of message dictionaries.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Message file not found: {file_path}")

        with open(path) as f:
            data = json.load(f)

        # Handle both single message and array of messages
        if isinstance(data, dict):
            messages = [data]
        elif isinstance(data, list):
            messages = data
        else:
            raise ValueError("Invalid message format: expected dict or list")

        logger.info(f"Loaded {len(messages)} messages from {file_path}")
        return messages

    def validate_message(self, message: dict[str, Any]) -> bool:
        """Validate message structure.

        Args:
            message: Message dictionary to validate.

        Returns:
            True if valid, False otherwise.
        """
        required_fields = ["message_id", "url", "author", "timestamp", "content"]
        for field in required_fields:
            if field not in message:
                logger.warning(f"Message missing required field: {field}")
                return False

        if not message["content"].strip():
            logger.warning(f"Message {message['message_id']} has empty content")
            return False

        return True

    def process_message(self, message: dict[str, Any]) -> None:
        """Process and ingest a single message.

        Args:
            message: Message dictionary to process.
        """
        if not self.validate_message(message):
            logger.warning(
                f"Skipping invalid message: {message.get('message_id', 'unknown')}"
            )
            return

        # Extract fields
        message_id = message["message_id"]
        content = message["content"]
        url = message["url"]
        author = message["author"]
        timestamp = message["timestamp"]
        metadata_extra = message.get("metadata", {})

        # Build metadata for vector store
        metadata = {
            "url": url,
            "author": author,
            "timestamp": timestamp,
            "channel": metadata_extra.get("channel", "unknown"),
            "tags": ",".join(metadata_extra.get("tags", [])),
        }

        # Add to vector store
        self.vector_store.add_message(message_id, content, metadata)
        logger.debug(f"Processed message: {message_id}")

    def process_messages_batch(self, messages: list[dict[str, Any]]) -> int:
        """Process and ingest multiple messages in batch.

        Args:
            messages: List of message dictionaries to process.

        Returns:
            Number of successfully processed messages.
        """
        valid_messages = []
        message_ids = []
        contents = []
        metadatas = []

        for message in messages:
            if not self.validate_message(message):
                logger.warning(
                    f"Skipping invalid message: {message.get('message_id', 'unknown')}"
                )
                continue

            message_id = message["message_id"]
            content = message["content"]
            url = message["url"]
            author = message["author"]
            timestamp = message["timestamp"]
            metadata_extra = message.get("metadata", {})

            metadata = {
                "url": url,
                "author": author,
                "timestamp": timestamp,
                "channel": metadata_extra.get("channel", "unknown"),
                "tags": ",".join(metadata_extra.get("tags", [])),
            }

            message_ids.append(message_id)
            contents.append(content)
            metadatas.append(metadata)
            valid_messages.append(message)

        if valid_messages:
            self.vector_store.add_messages_batch(message_ids, contents, metadatas)
            logger.info(f"Processed {len(valid_messages)} messages in batch")

        return len(valid_messages)

    def ingest_from_file(self, file_path: str) -> int:
        """Load and ingest messages from JSON file.

        Args:
            file_path: Path to JSON file containing messages.

        Returns:
            Number of successfully processed messages.
        """
        messages = self.load_messages_from_file(file_path)
        return self.process_messages_batch(messages)
