"""Tests for intent detection."""

from astra_d.routing.intent import detect_intent
from astra_d.routing.types import Intent


def test_exit_intent():
    assert detect_intent("exit") is Intent.EXIT
    assert detect_intent("quit") is Intent.EXIT


def test_help_intent():
    assert detect_intent("help") is Intent.HELP


def test_note_intent():
    assert detect_intent("note add buy milk") is Intent.NOTE


def test_task_intent():
    assert detect_intent("task list") is Intent.TASK


def test_pdf_intent():
    assert detect_intent("pdf report.pdf") is Intent.DOCUMENT


def test_search_intent():
    assert detect_intent("search budget") is Intent.SEARCH


def test_memory_intent():
    assert detect_intent("remember I like coffee") is Intent.MEMORY


def test_chat_intent():
    assert detect_intent("Hello Astra") is Intent.CHAT


def test_whitespace_is_ignored():
    assert detect_intent("   help   ") is Intent.HELP


def test_case_insensitive():
    assert detect_intent("HeLp") is Intent.HELP