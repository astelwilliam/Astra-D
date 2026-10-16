# Contributing to Astra-D

Thanks for contributing to Astra-D, a local AI assistant powered by Ollama. This guide gets you set up fast.

## Ways to contribute

- **Code** — new commands, new features, bug fixes
- **Docs** — README, guides, command help text
- **Bug reports** — open an issue with steps to reproduce plus your OS and Python version
- **Ideas** — open an issue to discuss before building big features

## Getting started

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running
- Git

### 1. Fork and clone

```bash
git clone https://github.com/<your-username>/Astra-D.git
cd Astra-D
```

### 2. Set up the environment

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Pull the model

```bash
ollama pull qwen2.5:3b
```

### 4. Run it

```bash
python main.py
```

## Running tests

```bash
python -m unittest discover -s tests -v
```

Tests redirect the `data/` directory via the `ASTRA_D_DATA_DIR` environment variable, so they never touch your real notes and tasks. Add tests for new commands and bug fixes.

## Code style

- Standard library first — the only third-party dependency is `ollama`
- Type hints on new functions (`from __future__ import annotations` is already used)
- Keep modules focused: one concern per file (`notes.py`, `tasks.py`, `memory.py`, …)
- User-facing errors should be clear one-liners, not tracebacks

## Data files

`data/memory.json`, `data/notes.json`, and `data/tasks.json` are gitignored and created automatically on first use. Never commit real data files.

## Submitting a pull request

1. Create a feature branch: `git checkout -b feat/short-description`
2. Commit with clear messages (`feat:`, `fix:`, `docs:`, `test:` prefixes)
3. Push to your fork and open a PR against `main`
4. Describe what changed and how you tested it (include test output for new commands)

## Questions?

Open an issue — the fastest way to reach the maintainer.
