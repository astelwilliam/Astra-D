# ADR-001: Memory Category System

- **Status:** Accepted
- **Date:** 2026-07-13
- **Version:** v0.10.0

---

# Context

Astra-D extracts long-term memories from conversations.

Each extracted memory must be classified into a single category before it can be scored, routed, and stored.

The category system is a core architectural decision because it directly affects:

- Memory Classification
- Importance Scoring
- Memory Routing
- Persistent Storage
- Retrieval
- Context Building

Changing the category system after persistent storage exists would require data migration and could invalidate historical memories.

Therefore the category system is frozen for the v0.10.x release series.

---

# Decision

Each stored memory belongs to exactly one category.

The categories are:

| Category | Description |
|----------|-------------|
| IGNORE | Information that should never become memory. |
| IDENTITY | Stable facts about the user. |
| PREFERENCE | Likes, dislikes and personal preferences. |
| GOAL | Long-term objectives and ambitions. |
| PROJECT | Information related to ongoing projects. |
| RELATIONSHIP | Information about people connected to the user. |
| FACT | General factual information worth remembering. |
| EVENT | Time-related events and milestones. |
| EMOTION | Temporary emotional state. |
| TASK | User-mentioned tasks and intentions. |

---

# Rules

## One Category Per Memory

A MemoryCandidate produces exactly one MemoryCategory.

If a user message contains multiple memories, the FactExtractor is responsible for splitting the message into multiple MemoryCandidates before classification.

Example:

User:

> I am a software developer and I love Python.

Produces:

MemoryCandidate #1

Category:

IDENTITY

Content:

"I am a software developer."

MemoryCandidate #2

Category:

PREFERENCE

Content:

"I love Python."

---

## Removed Categories

### TEMPORARY

Removed.

Temporary information is handled by retention policies rather than a dedicated category.

---

### KNOWLEDGE

Renamed to FACT.

The new name better represents factual information stored by Astra-D.

---

# Special Handling

## EMOTION

Emotion memories represent temporary emotional state.

Examples:

- I am stressed today.
- I feel tired.
- I am excited.

These memories should have shorter retention than other categories.

They should rarely influence long-term context.

---

## TASK

TASK represents that the user mentioned a task.

It is NOT the task management system.

The dedicated task subsystem remains responsible for task execution and reminders.

Future versions may automatically forward TASK memories into the task subsystem.

---

# Alternatives Considered

## Multiple Categories Per Memory

Rejected.

Reason:

Multiple labels significantly increase storage complexity, retrieval complexity, update resolution complexity and testing complexity.

Instead, compound statements are split into multiple MemoryCandidates.

---

## Dynamic Categories

Rejected.

Reason:

Stable enumerations provide predictable behaviour, simpler validation and easier storage.

---

# Consequences

## Advantages

- Simple classifier implementation
- Stable storage schema
- Easier retrieval
- Predictable scoring
- Straightforward testing

## Trade-offs

- Compound statements require extraction into multiple candidates.
- Some semantic richness is intentionally sacrificed for architectural simplicity.

These trade-offs are acceptable for v0.10.x.

---

# Future Considerations

The following are intentionally postponed beyond v0.10.x:

- Hierarchical categories
- Subcategories
- Multiple labels
- User-defined categories

These features require additional research and are not part of the current architecture.