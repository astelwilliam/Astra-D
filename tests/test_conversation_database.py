"""Tests for ConversationDatabase."""

from conversation_database import ConversationDatabase


def test_create_conversation():
    db = ConversationDatabase(":memory:")

    conversation_id = db.create_conversation("Test Chat")

    assert isinstance(conversation_id, int)
    assert conversation_id > 0


def test_list_conversations():
    db = ConversationDatabase(":memory:")

    db.create_conversation("First")
    db.create_conversation("Second")

    conversations = db.list_conversations()

    assert len(conversations) == 2
    assert conversations[0]["title"] == "First"
    assert conversations[1]["title"] == "Second"


def test_add_message():
    db = ConversationDatabase(":memory:")

    cid = db.create_conversation("Chat")

    db.add_message(cid, "user", "Hello")

    messages = db.get_messages(cid)

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"


def test_multiple_messages():
    db = ConversationDatabase(":memory:")

    cid = db.create_conversation("Chat")

    db.add_message(cid, "user", "Hello")
    db.add_message(cid, "assistant", "Hi!")

    messages = db.get_messages(cid)

    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


def test_empty_conversation():
    db = ConversationDatabase(":memory:")

    cid = db.create_conversation("Empty")

    assert db.get_messages(cid) == []

def test_get_conversation():
    db = ConversationDatabase(":memory:")

    cid = db.create_conversation("Test Chat")

    conversation = db.get_conversation(cid)

    assert conversation is not None
    assert conversation["id"] == cid
    assert conversation["title"] == "Test Chat"


def test_get_conversation_not_found():
    db = ConversationDatabase(":memory:")

    assert db.get_conversation(999) is None


def test_get_last_conversation():
    db = ConversationDatabase(":memory:")

    first = db.create_conversation("First")
    second = db.create_conversation("Second")

    db.add_message(second, "user", "Hello")

    conversation = db.get_last_conversation()

    assert conversation is not None
    assert conversation["id"] == second
    assert conversation["title"] == "Second"


def test_delete_conversation():
    db = ConversationDatabase(":memory:")

    cid = db.create_conversation("Delete Me")

    db.delete_conversation(cid)

    assert db.get_conversation(cid) is None


def test_delete_conversation_deletes_messages():
    db = ConversationDatabase(":memory:")

    cid = db.create_conversation("Chat")

    db.add_message(cid, "user", "Hello")
    db.add_message(cid, "assistant", "Hi")

    db.delete_conversation(cid)

    assert db.get_messages(cid) == []


def test_get_messages_returns_timestamp():
    db = ConversationDatabase(":memory:")

    cid = db.create_conversation("Chat")

    db.add_message(cid, "user", "Hello")

    messages = db.get_messages(cid)

    assert "timestamp" in messages[0]