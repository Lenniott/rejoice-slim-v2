# 🎙️ Rejoice Slim v2

**Local-first voice transcription tool - terminal-only, privacy-first**

Rejoice = {record, jot, voice}  
Slim = {super lightweight, no UI, no cloud, no crazy}

## Purpose

Record voice, get accurate transcripts with AI summaries—all local, terminal-only, privacy-first.

## Core Principles

1. **Data Integrity Above All** - Never lose a transcript
2. **Simplicity Over Features** - One command to start, one key to stop
3. **Local-First, Local-Only** - No internet required (except Ollama install)
4. **Transparency Over Magic** - User always knows what's happening
5. **Boring Reliability Over Clever Features** - Code that just works

## Status

🚧 **In Development** - Phase 0: Installation & Environment Setup

## Installation

Coming soon! Installation script will be available in Phase 0.

## Quick Start

```bash
# Start recording
rec

# Press Enter to stop
# Transcript saved automatically
```

## Development

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Project Structure

```
rejoice-v2/
├── src/rejoice/          # Source code
├── tests/                # Test suite
├── docs/                 # Documentation
├── scripts/              # Installation scripts
└── pyproject.toml        # Package configuration
```

## Technology Stack

- **faster-whisper** - Transcription engine (4x faster than openai-whisper)
- **sounddevice** - Audio recording
- **ollama** - Local AI enhancement
- **rich** - Terminal UI
- **click** - CLI framework

## Documentation

- [VISION.md](docs/VISION.md) - Product philosophy & scope
- [REWRITE_PLAN.md](docs/REWRITE_PLAN.md) - Technical architecture
- [BACKLOG.md](docs/BACKLOG.md) - User stories & tasks

## License

MIT License

