# Astra-D Architecture

```
                 User
                   │
                   ▼
               main.py
                   │
                   ▼
           PromptBuilder
                   │
                   ▼
          RetrievalEngine
                   │
                   ▼
        memory_retrieval.py
                   │
                   ▼
             ranking.py
                   │
                   ▼
          SemanticMemory
                   │
          ┌────────┴────────┐
          ▼                 ▼
     SQLite DB        Document Store
                              │
                              ▼
                           ChromaDB
```

## Core Modules

- main.py
- memory_engine.py
- semantic_memory.py
- memory_database.py
- memory_retrieval.py
- ranking.py
- retrieval_engine.py
- prompt_builder.py
- retrieval.py
- notes.py
- tasks.py
- filesearch.py

Current Status:
- Modular
- Test-driven
- Local-first
- Persistent Memory