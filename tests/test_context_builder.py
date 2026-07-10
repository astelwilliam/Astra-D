"""Tests for the context builder."""

from astra_d.context.builder import ContextBuilder
from astra_d.routing.types import Intent


def test_chat_has_empty_context():
    builder = ContextBuilder()

    context = builder.build(
        intent=Intent.CHAT,
        message="Hello"
    )

    assert context.memories == []
    assert context.documents == []
    assert context.notes == []
    assert context.tasks == []


def test_memory_intent_requests_memories():
    builder = ContextBuilder()

    context = builder.build(
        intent=Intent.MEMORY,
        message="What GPU do I own?"
    )

    assert context.use_memory is True


def test_document_intent_requests_documents():
    builder = ContextBuilder()

    context = builder.build(
        intent=Intent.DOCUMENT,
        message="Summarize the PDF"
    )

    assert context.use_documents is True


def test_task_intent_requests_tasks():
    builder = ContextBuilder()

    context = builder.build(
        intent=Intent.TASK,
        message="Show my tasks"
    )

    assert context.use_tasks is True


def test_note_intent_requests_notes():
    builder = ContextBuilder()

    context = builder.build(
        intent=Intent.NOTE,
        message="Show my notes"
    )

    assert context.use_notes is True