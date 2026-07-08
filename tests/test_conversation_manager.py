from astra_d.conversation.database import ConversationDatabase
from astra_d.conversation.manager import ConversationManager


def test_new_conversation():
    db = ConversationDatabase(":memory:")
    manager = ConversationManager(db)

    cid = manager.new_conversation("Test Chat")

    assert isinstance(cid, int)
    assert cid > 0


def test_get_active_conversation():
    db = ConversationDatabase(":memory:")
    manager = ConversationManager(db)

    cid = manager.new_conversation("Test Chat")

    assert manager.get_active_conversation() == cid

def test_add_user_message():
    db = ConversationDatabase(":memory:")
    manager = ConversationManager(db)

    manager.new_conversation("Chat")

    manager.add_user_message("Hello")

    history = manager.get_history()

    assert len(history) == 1
    assert history[0]["role"] == "user"


def test_add_assistant_message():
    db = ConversationDatabase(":memory:")
    manager = ConversationManager(db)

    manager.new_conversation("Chat")

    manager.add_assistant_message("Hi!")

    history = manager.get_history()

    assert history[0]["role"] == "assistant"


def test_get_history_empty():
    db = ConversationDatabase(":memory:")
    manager = ConversationManager(db)

    manager.new_conversation("Chat")

    assert manager.get_history() == []


def test_open_conversation():
    db = ConversationDatabase(":memory:")
    manager = ConversationManager(db)

    cid = manager.new_conversation("Chat")

    manager.open_conversation(cid)

    assert manager.get_active_conversation() == cid


def test_list_conversations():
    db = ConversationDatabase(":memory:")
    manager = ConversationManager(db)

    manager.new_conversation("First")
    manager.new_conversation("Second")

    conversations = manager.list_conversations()

    assert len(conversations) == 2
    assert conversations[0]["title"] == "First"
    assert conversations[1]["title"] == "Second"


def test_resume_last_conversation():
    db = ConversationDatabase(":memory:")
    manager = ConversationManager(db)

    first = manager.new_conversation("First")
    second = manager.new_conversation("Second")

    resumed = manager.resume_last_conversation()

    assert resumed == second
    assert manager.get_active_conversation() == second


def test_delete_conversation():
    db = ConversationDatabase(":memory:")
    manager = ConversationManager(db)

    cid = manager.new_conversation("Delete Me")

    manager.delete_conversation(cid)

    assert manager.get_active_conversation() is None
    assert db.get_conversation(cid) is None