<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# RAG Chatbot Project

## Project Overview

This is a Python-based RAG (Retrieval-Augmented Generation) CLI chatbot with MongoDB integration, using uv as the dependency manager.

### Tech Stack
- **Language**: Python 3.10+
- **Dependency Manager**: UV
- **Database**: MongoDB
- **LLM**: OpenAI (configurable)
- **CLI Framework**: Click
- **Testing**: Pytest
- **Embeddings**: Sentence Transformers

## Project Structure

```
src/rag_chatbot/
├── __init__.py           # Package initialization
├── config/              # Configuration management
│   ├── __init__.py
│   └── settings.py      # Pydantic settings
├── db/                  # Database layer
│   ├── __init__.py
│   └── mongodb.py       # MongoDB client
├── core/                # Core RAG components
│   ├── __init__.py
│   ├── embeddings.py    # Embedding manager
│   ├── retriever.py     # Document retriever
│   └── qa_chain.py      # QA generation
├── cli/                 # CLI interface
│   ├── __init__.py
│   └── main.py          # CLI commands
└── utils/               # Utilities
    ├── __init__.py
    └── logging.py       # Logging setup

tests/                   # Test suite
├── __init__.py
└── test_embeddings.py   # Embedding tests
```

## Key Components

### Configuration (config/settings.py)
- Manages MongoDB URI, OpenAI API key, embedding models
- Uses Pydantic for validation
- Loads from .env file

### Database Layer (db/mongodb.py)
- MongoDBClient class for database operations
- Stores conversations and documents
- Full-text search capabilities
- Index management

### Core RAG Pipeline
- **EmbeddingManager**: Generate embeddings using SentenceTransformers
- **RAGRetriever**: Retrieve relevant documents from MongoDB
- **QAChain**: Generate answers using OpenAI with retrieved context

### CLI Interface (cli/main.py)
Commands:
- `chat` - Interactive chat session
- `load-documents` - Load documents into MongoDB
- `clear-history` - Clear conversation history

## Getting Started

1. **Setup virtual environment with UV**:
   ```bash
   uv venv
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and MongoDB URI
   ```

4. **Start chatbot**:
   ```bash
   python -m rag_chatbot.cli.main chat
   ```

## Development Guidelines

### Code Style
- Use black for formatting
- Use isort for import sorting
- Follow PEP 8
- Type hints required

### Adding Features
1. Add code to appropriate module (config, db, core, cli, or utils)
2. Write tests in tests/ directory
3. Update __init__.py exports
4. Run tests: `pytest`
5. Check formatting: `black src/rag_chatbot && isort src/rag_chatbot`

### Testing
```bash
pytest                          # Run all tests
pytest --cov=src/rag_chatbot   # With coverage
pytest tests/test_*.py -v       # Verbose output
```

## Dependencies Management with UV

### Installing packages
```bash
uv pip install package_name
```

### Syncing dependencies
```bash
uv sync              # Install from lock file
uv sync --all-extras # Including dev dependencies
```

### Adding to pyproject.toml
- Regular dependencies in `[project]` section
- Dev dependencies in `[project.optional-dependencies]` dev section

## Environmental Variables

See `.env.example` for all available configuration options:
- MONGODB_URI
- MONGODB_DB_NAME
- OPENAI_API_KEY
- OPENAI_MODEL
- EMBEDDING_MODEL
- LOG_LEVEL
- MAX_HISTORY
- CHUNK_SIZE
- CHUNK_OVERLAP

## Common Tasks

### Running tests
```bash
pytest
pytest --cov
```

### Code quality checks
```bash
black src/rag_chatbot tests
isort src/rag_chatbot tests
flake8 src/rag_chatbot
mypy src/rag_chatbot
```

### Interactive development
```bash
python -m rag_chatbot.cli.main chat
```

## Debugging

Enable debug logging:
```bash
LOG_LEVEL=DEBUG python -m rag_chatbot.cli.main chat
```

## MongoDB Local Setup

```bash
# Install (macOS)
brew install mongodb-community

# Start service
brew services start mongodb-community

# Or run manually
mongod
```

## Next Steps

- [ ] Install dependencies with UV
- [ ] Configure .env file with API keys
- [ ] Test MongoDB connection
- [ ] Load sample documents
- [ ] Run interactive chat
- [ ] Extend with custom embedding models
- [ ] Add more CLI commands
