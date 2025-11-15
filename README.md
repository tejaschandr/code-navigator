# Codebase Navigator

My attempt at a CLI tool because I don't like copilot

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/download)

## Installation
```bash
# Install from GitHub
pip install git+https://github.com/tejaschandr/code-navigator.git

# Pull required models
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

## Usage
```bash
# Index a codebase
nav index /path/to/project

# Ask questions
nav ask "what files are in this codebase"

# Interactive chat
nav chat

# List indexed projects
nav list

# Clean up
nav clean --all
```

## How it Works

1. Scans code files and chunks them by function/class
2. Generates embeddings using Ollama's nomic-embed-text
3. Stores in local ChromaDB vector database
4. Answers questions using qwen2.5:7b LLM

All data stays on your machine. Completely offline after initial setup.