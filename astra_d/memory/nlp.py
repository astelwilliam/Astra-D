"""Lightweight NLP preprocessing built on spaCy.

Standalone, dependency-light module. Loads the spaCy model exactly once
at import time and exposes analyze() as the single public entry point.
This will later back Astra-D's semantic memory engine, but is not wired
into memory.py, retrieval.py, or main.py yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import spacy

# Loaded once at import time. Never call spacy.load() inside a function.
_NLP = spacy.load("en_core_web_sm")

_KEEP_POS = {"NOUN", "PROPN", "VERB", "ADJ"}


@dataclass(frozen=True)
class NLPResult:
    """Structured output of analyze()."""

    text: str
    entities: list[dict] = field(default_factory=list)
    noun_chunks: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


def extract_entities(doc: "spacy.tokens.Doc") -> list[dict]:
    """Return named entities as {"text": ..., "label": ...} dicts."""
    return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]


def extract_noun_chunks(doc: "spacy.tokens.Doc") -> list[str]:
    """Return noun chunks as plain strings."""
    return [chunk.text for chunk in doc.noun_chunks]


def extract_keywords(doc: "spacy.tokens.Doc") -> list[str]:
    """Return unique lemmatized keywords, order preserved.

    Keeps only NOUN / PROPN / VERB / ADJ tokens, drops stop words,
    punctuation, and whitespace-only tokens, and uses the lemma
    instead of the surface form (e.g. "running" -> "run").
    """
    keywords: list[str] = []
    seen: set[str] = set()

    for token in doc:
        if token.is_stop or token.is_punct or token.is_space:
            continue
        if token.pos_ not in _KEEP_POS:
            continue

        lemma = token.lemma_.strip().lower()
        if not lemma:
            continue
        if lemma in seen:
            continue

        seen.add(lemma)
        keywords.append(lemma)

    return keywords


def analyze(text: str) -> NLPResult:
    """Run entity, noun-chunk, and keyword extraction over text."""
    if not text or not text.strip():
        return NLPResult(text=text, entities=[], noun_chunks=[], keywords=[])

    doc = _NLP(text)

    return NLPResult(
        text=text,
        entities=extract_entities(doc),
        noun_chunks=extract_noun_chunks(doc),
        keywords=extract_keywords(doc),
    )