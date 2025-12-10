"""Vector store implementation using ChromaDB."""

from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer

from ..utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Vector database for storing and retrieving message embeddings."""

    def __init__(
        self,
        persist_directory: str = "data/embeddings",
        collection_name: str = "message_embeddings",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        """Initialize vector store.

        Args:
            persist_directory: Directory to persist vector database.
            collection_name: Name of the collection.
            embedding_model: Name of the sentence transformer model.
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"Initialized vector store with collection: {collection_name}")

    def add_message(
        self, message_id: str, content: str, metadata: dict[str, Any]
    ) -> None:
        """Add a message to the vector store.

        Args:
            message_id: Unique message identifier.
            content: Message content to embed.
            metadata: Metadata to store with the message.
        """
        # Generate embedding
        embedding = self.embedding_model.encode(content).tolist()

        # Add to collection
        self.collection.add(
            ids=[message_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
        )
        logger.debug(f"Added message {message_id} to vector store")

    def add_messages_batch(
        self,
        message_ids: list[str],
        contents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        """Add multiple messages to the vector store in batch.

        Args:
            message_ids: List of unique message identifiers.
            contents: List of message contents to embed.
            metadatas: List of metadata dictionaries.
        """
        # Generate embeddings in batch
        embeddings = self.embedding_model.encode(contents).tolist()

        # Add to collection
        self.collection.add(
            ids=message_ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas,
        )
        logger.info(f"Added {len(message_ids)} messages to vector store")

    def search(
        self,
        query: str,
        top_k: int = 3,
        min_similarity: float | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar messages.

        Args:
            query: Query text to search for.
            top_k: Number of top results to return.
            min_similarity: Minimum similarity score (0-1).

        Returns:
            List of result dictionaries with id, content, metadata, and score.
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()

        # Search collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                # ChromaDB returns distances, convert to similarity score
                # For cosine distance: similarity = 1 - distance
                distance = results["distances"][0][i] if results["distances"] else 0
                similarity = 1 - distance

                # Filter by minimum similarity if specified
                if min_similarity is not None and similarity < min_similarity:
                    continue

                result = {
                    "id": results["ids"][0][i],
                    "content": (
                        results["documents"][0][i] if results["documents"] else ""
                    ),
                    "metadata": (
                        results["metadatas"][0][i] if results["metadatas"] else {}
                    ),
                    "score": similarity,
                }
                formatted_results.append(result)

        logger.debug(f"Search returned {len(formatted_results)} results for query")
        return formatted_results

    def delete_message(self, message_id: str) -> None:
        """Delete a message from the vector store.

        Args:
            message_id: Message identifier to delete.
        """
        self.collection.delete(ids=[message_id])
        logger.debug(f"Deleted message {message_id} from vector store")

    def clear(self) -> None:
        """Clear all messages from the collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Cleared vector store collection")

    def count(self) -> int:
        """Get count of messages in the collection.

        Returns:
            Number of messages stored.
        """
        return self.collection.count()
