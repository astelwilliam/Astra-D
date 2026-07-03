"""Tests for memory_nlp.py."""

from __future__ import annotations

import memory_nlp


def test_entity_extraction():
    result = memory_nlp.analyze("Barack Obama was born in Hawaii.")
    labels = {(e["text"], e["label"]) for e in result.entities}
    assert ("Barack Obama", "PERSON") in labels
    assert any(e["label"] == "GPE" for e in result.entities)


def test_noun_chunk_extraction():
    result = memory_nlp.analyze("The quick brown fox jumps over the lazy dog.")
    assert any("fox" in chunk for chunk in result.noun_chunks)
    assert any("dog" in chunk for chunk in result.noun_chunks)


def test_keyword_extraction_filters_stopwords_and_punct():
    result = memory_nlp.analyze("The cat is sitting on the mat, quietly.")
    assert "the" not in result.keywords
    assert "is" not in result.keywords
    assert "," not in result.keywords
    assert "cat" in result.keywords
    assert "sit" in result.keywords
    assert "mat" in result.keywords


def test_empty_string_handling():
    result = memory_nlp.analyze("")
    assert result.entities == []
    assert result.noun_chunks == []
    assert result.keywords == []


def test_whitespace_only_string_handling():
    result = memory_nlp.analyze("   \n\t  ")
    assert result.entities == []
    assert result.noun_chunks == []
    assert result.keywords == []


def test_repeated_words_do_not_duplicate_keywords():
    result = memory_nlp.analyze("Run run running runs run.")
    # All forms lemmatize to "run"; should appear exactly once.
    assert result.keywords.count("run") == 1


def test_lemmatization_normalizes_surface_forms():
    result = memory_nlp.analyze("The cars were running fast near the running cats.")
    assert "car" in result.keywords
    assert "run" in result.keywords
    assert "cat" in result.keywords
    # Surface forms should not leak through.
    assert "cars" not in result.keywords
    assert "running" not in result.keywords
    assert "cats" not in result.keywords


def test_keyword_order_is_preserved():
    result = memory_nlp.analyze("Apples grow on trees. Trees need water.")
    # "trees" (as tree) appears before "water" in the source text.
    assert result.keywords.index("tree") < result.keywords.index("water")


def test_analyze_returns_nlpresult_dataclass():
    result = memory_nlp.analyze("Simple sentence.")
    assert isinstance(result, memory_nlp.NLPResult)
    assert result.text == "Simple sentence."