# Message RAG System

RAG system that processes messages and answers questions with source attribution.

![Untitledfo](https://github.com/user-attachments/assets/fabbf186-bf85-4b85-a2de-af1c2ecc15b8)

<img width="1892" height="1043" alt="Screenshot 2025-12-10 at 15 45 36" src="https://github.com/user-attachments/assets/4a31b448-1b1e-44e6-a4d1-2c2a35de59d3" />


## Install

```bash
cd message_rag
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

## Quick Start

### Easy Launch (Mac - Double Click)

1. Double-click **`Start Message RAG.command`**
2. Browser opens automatically

### Terminal Launch

```bash
./run.sh      # Start (checks port, installs deps, opens browser)
./stop.sh     # Stop
```

## Usage

### Web Interface (GUI)

**Recommended method:** Use the launcher above, or manually:

```bash
streamlit run src/web_app.py
```

Features:
- Chat-based interface
- File upload for message ingestion
- Real-time query with source display
- Database statistics and management

### Command Line Interface (CLI)

```bash
# Ingest messages from JSON file
python -m src.cli ingest examples/sample_messages.json

# Query the system
python -m src.cli query "What was discussed about the budget?"

# Interactive mode
python -m src.cli interactive

# View statistics
python -m src.cli stats

# Clear database
python -m src.cli clear
```

## Config

Edit [config/model_config.yaml](config/model_config.yaml):
- `model_name`: claude-sonnet-4-5 | gpt-4
- `temperature`: 0.0-1.0
- `max_tokens`: up to 4096
- `top_k`: number of messages to retrieve
- `min_similarity_score`: 0.0-1.0

## Message Format

```json
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
```

## Project Structure

```
src/
├── llm/        # LLM clients
├── prompts/    # Prompt management
├── rag/        # Vector store, message processing, query engine
├── utils/      # Rate limiter, cache, tokens, logger
└── handlers/   # Error handling
```

## Tests

```bash
pytest tests/ -v
```

## License

MIT
