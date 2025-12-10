"""Command-line interface for Message RAG system."""

import argparse
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

from .llm.claude_client import ClaudeClient
from .rag.message_processor import MessageProcessor
from .rag.query_engine import QueryEngine
from .rag.vector_store import VectorStore
from .utils.logger import get_logger, setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = get_logger(__name__)


class MessageRAGCLI:
    """CLI for Message RAG system."""

    def __init__(self, config_path: str = "config/model_config.yaml") -> None:
        """Initialize CLI.

        Args:
            config_path: Path to model configuration file.
        """
        # Load configuration
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Initialize components
        self.vector_store: VectorStore | None = None
        self.message_processor: MessageProcessor | None = None
        self.query_engine: QueryEngine | None = None
        self.llm_client: ClaudeClient | None = None

        logger.info("Initialized Message RAG CLI")

    def initialize_components(self) -> None:
        """Initialize RAG system components."""
        if self.vector_store is not None:
            return  # Already initialized

        # Initialize vector store
        vector_db_config = self.config["vector_db"]
        embedding_config = self.config["embedding"]

        self.vector_store = VectorStore(
            persist_directory=vector_db_config["persist_directory"],
            collection_name=vector_db_config["collection_name"],
            embedding_model=embedding_config["model"],
        )

        # Initialize message processor
        self.message_processor = MessageProcessor(self.vector_store)

        # Initialize LLM client
        model_config = self.config["models"][self.config["models"]["default"]]
        self.llm_client = ClaudeClient(model_config)

        # Initialize query engine
        rag_config = self.config["rag"]
        self.query_engine = QueryEngine(
            llm_client=self.llm_client,
            vector_store=self.vector_store,
            top_k=rag_config["top_k"],
            min_similarity=rag_config["min_similarity_score"],
        )

        logger.info("All components initialized")

    def ingest_command(self, file_path: str) -> None:
        """Ingest messages from JSON file.

        Args:
            file_path: Path to JSON file containing messages.
        """
        self.initialize_components()

        if not Path(file_path).exists():
            print(f"Error: File not found: {file_path}")
            sys.exit(1)

        print(f"Ingesting messages from {file_path}...")
        count = self.message_processor.ingest_from_file(file_path)
        print(f"Successfully ingested {count} messages")
        print(f"Total messages in database: {self.vector_store.count()}")

    def query_command(self, question: str) -> None:
        """Query the RAG system.

        Args:
            question: User's question.
        """
        self.initialize_components()

        if self.vector_store.count() == 0:
            print("Error: No messages in database. Please ingest messages first.")
            sys.exit(1)

        print(f"\nQuestion: {question}\n")
        print("Searching and generating answer...\n")

        response = self.query_engine.query(question)
        formatted = self.query_engine.format_response(response)

        print(formatted)

    def interactive_command(self) -> None:
        """Start interactive query mode."""
        self.initialize_components()

        if self.vector_store.count() == 0:
            print("Error: No messages in database. Please ingest messages first.")
            sys.exit(1)

        print("\n=== Message RAG Interactive Mode ===")
        print(f"Total messages in database: {self.vector_store.count()}")
        print("Type your questions (or 'quit' to exit)\n")

        while True:
            try:
                question = input("Question: ").strip()

                if question.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break

                if not question:
                    continue

                print("\nSearching and generating answer...\n")
                response = self.query_engine.query(question)
                formatted = self.query_engine.format_response(response)
                print(formatted)
                print("\n" + "=" * 50 + "\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                print(f"Error: {e}\n")

    def stats_command(self) -> None:
        """Display database statistics."""
        self.initialize_components()

        count = self.vector_store.count()
        print("\n=== Message Database Statistics ===")
        print(f"Total messages: {count}")
        print(f"Collection: {self.vector_store.collection_name}")
        print(f"Persist directory: {self.vector_store.persist_directory}")

    def clear_command(self) -> None:
        """Clear all messages from database."""
        self.initialize_components()

        confirm = input("Are you sure you want to clear all messages? (yes/no): ")
        if confirm.lower() == "yes":
            self.vector_store.clear()
            print("All messages cleared from database")
        else:
            print("Operation cancelled")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Message RAG System - Answer questions based on message history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Ingest command
    ingest_parser = subparsers.add_parser(
        "ingest", help="Ingest messages from JSON file"
    )
    ingest_parser.add_argument("file", help="Path to JSON file containing messages")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query the RAG system")
    query_parser.add_argument("question", help="Question to ask")

    # Interactive command
    subparsers.add_parser("interactive", help="Start interactive query mode")

    # Stats command
    subparsers.add_parser("stats", help="Display database statistics")

    # Clear command
    subparsers.add_parser("clear", help="Clear all messages from database")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize CLI
    cli = MessageRAGCLI()

    # Execute command
    try:
        if args.command == "ingest":
            cli.ingest_command(args.file)
        elif args.command == "query":
            cli.query_command(args.question)
        elif args.command == "interactive":
            cli.interactive_command()
        elif args.command == "stats":
            cli.stats_command()
        elif args.command == "clear":
            cli.clear_command()
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
