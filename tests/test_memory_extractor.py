from astra_d.memory.extractor import FactExtractor
from astra_d.memory.models import MemoryCandidate


def test_extractor_can_be_created():
    extractor = FactExtractor()

    assert extractor is not None


def test_extract_returns_list():
    extractor = FactExtractor()

    result = extractor.extract("Hello")

    assert isinstance(result, list)


def test_extract_returns_memory_candidate():
    extractor = FactExtractor()

    result = extractor.extract("I like coffee.")

    assert len(result) == 1
    assert isinstance(result[0], MemoryCandidate)


def test_extract_preserves_content():
    extractor = FactExtractor()

    message = "I want to become a software engineer."

    result = extractor.extract(message)

    assert result[0].content == message


def test_extract_sets_source():
    extractor = FactExtractor()

    result = extractor.extract("Hello")

    assert result[0].source == "conversation"


def test_extract_empty_string_returns_empty_list():
    extractor = FactExtractor()

    result = extractor.extract("")

    assert result == []


def test_extract_whitespace_returns_empty_list():
    extractor = FactExtractor()

    result = extractor.extract("     ")

    assert result == []