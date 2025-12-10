"""Streamlit web interface for Message RAG system."""

import sys
from pathlib import Path
from typing import Any

import streamlit as st
import yaml
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.claude_client import ClaudeClient
from src.rag.message_processor import MessageProcessor
from src.rag.query_engine import QueryEngine
from src.rag.vector_store import VectorStore
from src.utils.logger import get_logger, setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = get_logger(__name__)


def load_config() -> dict[str, Any]:
    """Load configuration from YAML file.

    Returns:
        Configuration dictionary.
    """
    with open("config/model_config.yaml") as f:
        return yaml.safe_load(f)


@st.cache_resource
def initialize_components() -> tuple[VectorStore, MessageProcessor, QueryEngine]:
    """Initialize RAG system components (cached).

    Returns:
        Tuple of (vector_store, message_processor, query_engine).
    """
    config = load_config()

    # Initialize vector store
    vector_db_config = config["vector_db"]
    embedding_config = config["embedding"]

    vector_store = VectorStore(
        persist_directory=vector_db_config["persist_directory"],
        collection_name=vector_db_config["collection_name"],
        embedding_model=embedding_config["model"],
    )

    # Initialize message processor
    message_processor = MessageProcessor(vector_store)

    # Initialize LLM client
    model_config = config["models"][config["models"]["default"]]
    llm_client = ClaudeClient(model_config)

    # Initialize query engine
    rag_config = config["rag"]
    query_engine = QueryEngine(
        llm_client=llm_client,
        vector_store=vector_store,
        top_k=rag_config["top_k"],
        min_similarity=rag_config["min_similarity_score"],
    )

    return vector_store, message_processor, query_engine


def main() -> None:
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Message RAG System",
        page_icon="💬",
        layout="wide",
    )

    st.title("💬 Message RAG System")
    st.markdown(
        "Ask questions about your message history and get answers with source attribution."
    )

    # Initialize components
    try:
        vector_store, message_processor, query_engine = initialize_components()
    except Exception as e:
        st.error(f"Failed to initialize system: {e}")
        st.info(
            "Make sure you have set ANTHROPIC_API_KEY in your .env file and are running from the message_rag directory."
        )
        return

    # Sidebar
    with st.sidebar:
        st.header("⚙️ System")

        # Stats
        message_count = vector_store.count()
        st.metric("Total Messages", message_count)

        st.markdown("---")

        # File upload
        st.subheader("📤 Ingest Messages")
        uploaded_file = st.file_uploader(
            "Upload JSON file",
            type=["json"],
            help="Upload a JSON file containing messages",
        )

        if uploaded_file is not None:
            if st.button("Ingest Messages"):
                try:
                    # Save uploaded file temporarily
                    temp_path = Path("data/outputs/temp_upload.json")
                    temp_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Ingest messages
                    count = message_processor.ingest_from_file(str(temp_path))

                    st.success(f"Successfully ingested {count} messages!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error ingesting messages: {e}")

        st.markdown("---")

        # Clear database
        st.subheader("🗑️ Clear Database")
        if st.button("Clear All Messages", type="secondary"):
            if message_count > 0:
                vector_store.clear()
                st.success("Database cleared!")
                st.rerun()
            else:
                st.info("Database is already empty")

        st.markdown("---")

        # Examples
        st.subheader("💡 Example Query")
        with st.expander("📋 See Input/Output Format", expanded=False):
            st.markdown("### Input Format")
            st.code(
                """{
  "message_id": "msg_001",
  "url": "https://example.com/messages/msg_001",
  "author": "John Doe",
  "timestamp": "2025-01-15T10:30:00Z",
  "content": "Message text here...",
  "metadata": {
    "channel": "general",
    "tags": ["important"]
  }
}""",
                language="json",
            )

            st.markdown("### Example Query & Response")
            st.markdown("**Query:** `What was discussed about the budget?`")
            st.markdown("**Expected Response:**")
            st.code(
                """Answer: The team discussed allocating $50k for development and $20k for marketing. The timeline was set for Q2 2025.

Sources:
- Budget allocation discussion by John (https://example.com/messages/msg_001)
- Timeline proposal by Sarah (https://example.com/messages/msg_002)""",
                language="text",
            )

            st.markdown(
                """
                **Try these queries:**
                - What was discussed about the budget?
                - Who mentioned authentication?
                - What are the performance metrics?
                - Tell me about user feedback
                """
            )

    # Query interface
    st.subheader("❓ Ask a Question")

    # Show warning if no messages
    if message_count == 0:
        st.warning(
            "⚠️ No messages in database. Please upload examples/sample_messages.json from the sidebar first!"
        )
        with st.expander("📖 Getting Started Guide"):
            st.markdown(
                """
            ### Quick Start

            1. In the sidebar, click "Browse files" under **📤 Ingest Messages**
            2. Select `examples/sample_messages.json`
            3. Click "Ingest Messages" button
            4. Come back here and ask: "What was discussed about the budget?"

            ### Your Own Data Format
            ```json
            [
              {
                "message_id": "msg_001",
                "url": "https://example.com/messages/msg_001",
                "author": "John Doe",
                "timestamp": "2025-01-15T10:30:00Z",
                "content": "Message text here...",
                "metadata": {
                  "channel": "general",
                  "tags": ["important"]
                }
              }
            ]
            ```
            """
            )

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Query input
    if question := st.chat_input("Type your question here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("user"):
            st.markdown(question)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching and generating answer..."):
                try:
                    response = query_engine.query(question)

                    answer = response["answer"]

                    # Display answer (sources are already included in the answer)
                    st.markdown(answer)

                    # Add to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )

                except Exception as e:
                    error_msg = f"Error processing query: {e}"
                    st.error(error_msg)
                    logger.error(error_msg, exc_info=True)

    # Clear chat button
    if st.session_state.messages:
        if st.button("Clear Chat History", type="secondary"):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()
