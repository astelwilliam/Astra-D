# Astra-D

**Astra-D** is a local-first AI assistant powered by Ollama that combines conversational AI with persistent semantic memory, intelligent retrieval, note management, task management, and document search.

Unlike traditional chatbots, Astra-D remembers previous conversations, retrieves relevant memories, and uses them to generate context-aware responses while keeping your data entirely on your own machine.

---

# Features

## AI Conversation

- Interactive chat powered by Ollama
- Conversation history
- Context-aware responses
- Memory-augmented prompting

## Semantic Memory

- NLP-based memory extraction
- Persistent SQLite database
- Automatic memory restoration
- Memory retrieval by relevance
- Long-term conversational memory

## Productivity

- Notes management
- Task management
- Recursive file search

## Engineering

- Modular architecture
- SQLite persistence
- Test-driven development
- 58 automated unit tests

---

# Technology Stack

- Python 3.12
- Ollama
- SQLite
- spaCy
- Pytest
- Git

---

# Requirements

- Python 3.12+
- Ollama installed locally

---

# Installation

Clone the repository:

```bash
git clone https://github.com/astelwilliam/Astra-D.git
cd Astra-D
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment.

### Windows

```powershell
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Ollama Setup

Install Ollama:

https://ollama.com/download

Pull the required model:

```bash
ollama pull qwen2.5:3b
```

Verify:

```bash
ollama list
```

Start the Ollama service before launching Astra-D.

---

# Running Astra-D

```bash
python main.py
```

---

# Commands

## Chat

```text
astra-d> hello
astra-d> What is Python?
astra-d> history
astra-d> clear
```

Plain text is automatically treated as chat input.

---

## Notes

```text
astra-d> note add Buy groceries
astra-d> note list
astra-d> note delete <note-id>
```

---

## Tasks

```text
astra-d> task add Finish memory module
astra-d> task list
astra-d> task complete <task-id>
astra-d> task delete <task-id>
```

---

## File Search

```text
astra-d> search . readme
astra-d> search C:\Users\Astel\Documents report
```

---

## Exit

```text
astra-d> quit
```

---

# Project Structure

```text
Astra-D/
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   ├── CHANGELOG.md
│   ├── MEMORY.md
│   ├── API.md
│   └── CONTRIBUTING.md
│
├── tests/
├── data/
│
├── main.py
├── memory_engine.py
├── memory_database.py
├── semantic_memory.py
├── memory_nlp.py
├── retrieval.py
├── prompt_builder.py
├── notes.py
├── tasks.py
├── filesearch.py
├── requirements.txt
└── README.md
```

---

# Memory Architecture

```text
User Message
      │
      ▼
 NLP Analysis
      │
      ▼
 MemoryEntry
      │
      ▼
 Semantic Memory (RAM)
      │
      ▼
 SQLite Database
      │
      ▼
 Retrieval Engine
      │
      ▼
 Prompt Builder
      │
      ▼
 Ollama
      │
      ▼
 AI Response
```

---

# Documentation

The complete documentation is available in the `docs/` folder.

| Document | Description |
|----------|-------------|
| ARCHITECTURE.md | System architecture |
| ROADMAP.md | Development roadmap |
| CHANGELOG.md | Project history |
| MEMORY.md | Memory system |
| API.md | API reference |
| CONTRIBUTING.md | Contribution guide |

---

# Running Tests

Run the complete test suite:

```bash
pytest
```

Current status:

```text
58 Passed
0 Failed
```

---

# Environment Variables

| Variable | Description |
|----------|-------------|
| ASTRA_D_DATA_DIR | Override the default `data/` directory for testing |

---

# Current Version

**v0.6.0-alpha**

## Completed

- ✅ Interactive AI Chat
- ✅ Notes Management
- ✅ Task Management
- ✅ Recursive File Search
- ✅ Semantic Memory
- ✅ SQLite Persistence
- ✅ Automatic Memory Restoration
- ✅ Memory Retrieval
- ✅ Prompt Builder
- ✅ Memory-Augmented Chat
- ✅ 58 Passing Tests

---

# Roadmap

## v0.7.0-alpha

- Intelligent memory ranking
- Memory importance scoring
- Memory updating
- Memory decay
- User profile memory

## v0.8.0-alpha

- Python tool integration
- Web search
- PDF analysis
- OCR support
- Tool orchestration

## v0.9.0-alpha

- Autonomous planning
- Goal management
- Reflection system
- Workflow execution

## v1.0.0

- Fully autonomous local AI assistant
- Long-term personal knowledge
- Advanced reasoning
- Multi-agent architecture

---

# Development Principles

- Local-first
- Privacy-first
- Modular architecture
- Test-driven development
- Open source
- Extensible design

---

# License

This project is currently under active development.