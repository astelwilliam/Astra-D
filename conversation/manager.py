from conversation_database import ConversationDatabase


class ConversationManager:
    """Manage conversations and conversation state."""

    def __init__(self, database: ConversationDatabase) -> None:
        self._database = database
        self._active_conversation_id = None

    def new_conversation(self, title: str = "New Chat") -> int:
        """Create a new conversation and make it active."""
        conversation_id = self._database.create_conversation(title)
        self._active_conversation_id = conversation_id
        return conversation_id

    def get_active_conversation(self) -> int | None:
        """Return the active conversation ID."""
        return self._active_conversation_id

    def add_user_message(self, text: str) -> None:
        """Add a user message to the active conversation."""
        if self._active_conversation_id is None:
            raise RuntimeError("No active conversation.")

        self._database.add_message(
            self._active_conversation_id,
            "user",
            text,
        )

    def add_assistant_message(self, text: str) -> None:
        """Add an assistant message to the active conversation."""
        if self._active_conversation_id is None:
            raise RuntimeError("No active conversation.")

        self._database.add_message(
            self._active_conversation_id,
            "assistant",
            text,
        )

    def get_history(self) -> list[dict]:
        """Return the active conversation history."""
        if self._active_conversation_id is None:
            return []

        return self._database.get_messages(
            self._active_conversation_id
        )

    def open_conversation(self, conversation_id: int) -> None:
        """Open an existing conversation."""
        conversation = self._database.get_conversation(conversation_id)

        if conversation is None:
            raise ValueError("Conversation not found.")

        self._active_conversation_id = conversation_id

    def list_conversations(self) -> list[dict]:
        """Return all conversations."""
        return self._database.list_conversations()


    def resume_last_conversation(self) -> int | None:
        """Resume the most recently updated conversation."""
        conversation = self._database.get_last_conversation()
    
        if conversation is None:
            return None
    
        self._active_conversation_id = conversation["id"]
        return self._active_conversation_id
    
    
    def delete_conversation(self, conversation_id: int) -> None:
        """Delete a conversation."""
    
        self._database.delete_conversation(conversation_id)
    
        if self._active_conversation_id == conversation_id:
            self._active_conversation_id = None
    
    


    