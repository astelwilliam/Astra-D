# Memory Pipeline Architecture

**Status:** Draft (v0.10.0)

---

# Purpose

The Memory Pipeline is responsible for transforming raw user conversations into structured, persistent memories.

It is intentionally designed as a sequence of small, independent stages.

Each stage has a single responsibility.

Each stage communicates only through immutable data models.

No stage performs the responsibility of another.

---

# Pipeline Overview

```text
UserMessage
      │
      ▼
FactExtractor
      │
      ▼
MemoryCandidate
      │
      ▼
MemoryClassifier
      │
      ▼
MemoryDecision
      │
      ▼
ImportanceScorer
      │
      ▼
ImportanceScore
      │
      ▼
MemoryRouter
      │
      ▼
UpdateResolver
      │
      ▼
MemoryStore
```

Each stage consumes the output of the previous stage and produces data for the next stage.

---

# Pipeline Stages

## 1. FactExtractor

### Responsibility

Extract memory-worthy facts from a user message.

A single message may produce zero, one, or many MemoryCandidates.

### Input

UserMessage

### Output

list[MemoryCandidate]

### Depends On

- UserMessage

### Must Not Depend On

- Storage
- LLM providers
- Database
- Retrieval
- MemoryStore

### Failure Behaviour

If extraction fails:

- log the error
- return an empty list
- continue the conversation normally

---

## 2. MemoryClassifier

### Responsibility

Determine whether a candidate should become a memory and assign exactly one MemoryCategory.

### Input

MemoryCandidate

### Output

MemoryDecision

### Depends On

- MemoryCandidate
- MemoryCategory

### Must Not Depend On

- Storage
- Providers
- Retrieval
- Database

### Failure Behaviour

Return an IGNORE decision with an explanatory reason.

---

## 3. ImportanceScorer

### Responsibility

Estimate how valuable a memory is for long-term retention.

Importance scoring is deterministic in v0.10.x.

### Input

- MemoryCandidate
- MemoryDecision

### Output

ImportanceScore

### Depends On

- MemoryCandidate
- MemoryDecision

### Must Not Depend On

- MemoryStore
- Retrieval
- Providers
- Database
- Filesystem

### Failure Behaviour

Return a conservative default score and log the failure.

---

## 4. MemoryRouter

### Responsibility

Decide whether a memory continues through the pipeline.

The router applies routing rules but does not perform storage.

### Input

- MemoryDecision
- ImportanceScore

### Output

RoutingDecision

Examples:

- STORE
- DISCARD

### Depends On

- MemoryDecision
- ImportanceScore

### Must Not Depend On

- Storage implementation
- Providers

### Failure Behaviour

Discard the candidate and log the failure.

---

## 5. UpdateResolver

### Responsibility

Determine how a new memory relates to existing memories.

Possible outcomes include:

- CREATE
- UPDATE
- MERGE
- IGNORE

The UpdateResolver does not assign importance and does not classify memories.

### Input

- Incoming Memory
- Existing Memory (optional)

### Output

StorageAction

### Depends On

- Memory models
- MemoryStore interface

### Must Not Depend On

- Providers
- User interface
- Retrieval ranking

### Failure Behaviour

Prefer CREATE rather than losing information.

---

## 6. MemoryStore

### Responsibility

Persist memories.

MemoryStore performs no business logic.

It stores exactly what it receives.

### Input

StorageAction

### Output

Stored Memory

### Depends On

Storage implementation.

### Must Not Depend On

- Classifier
- Scorer
- Router
- Extractor

### Failure Behaviour

Return an explicit storage error.

Never silently lose data.

---

# Design Principles

The memory pipeline follows these principles.

## Single Responsibility

Each stage performs exactly one task.

---

## Immutable Data

Pipeline models are immutable.

Stages never modify objects created by previous stages.

Instead, they produce new objects.

---

## Stateless Components

Pipeline stages should be stateless whenever possible.

This makes testing deterministic and simplifies debugging.

---

## Deterministic Behaviour

Given identical input, a stage should produce identical output.

---

## Replaceable Implementations

Every stage communicates through an interface.

Future implementations may replace rule-based logic without changing callers.

Examples include:

- RuleBasedImportanceScorer
- MLImportanceScorer
- LLMImportanceScorer

---

## Failure Isolation

Failure in one stage should not crash the assistant.

Whenever possible:

- log the failure
- return a safe default
- continue execution

---

# Out of Scope

The following are intentionally excluded from v0.10.x:

- Machine learning scoring
- Automatic memory summarisation
- Memory decay
- Memory importance feedback loops
- Knowledge graph integration
- Multi-agent memory sharing

These features may be introduced in future versions without changing the pipeline architecture.

---

# Architecture Summary

The Memory Pipeline transforms conversations into persistent memories through a sequence of small, independent, testable components.

Each stage has a single responsibility.

Each stage communicates through immutable models.

Business logic is separated from persistence.

Implementations may evolve while the pipeline structure remains stable.