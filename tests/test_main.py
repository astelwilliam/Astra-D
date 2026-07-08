"""Tests for main.py command dispatch and Ollama integration."""

import os
import tempfile
import unittest
from unittest.mock import patch



import main
import memory
import notes
import tasks


from astra_d.conversation.database import ConversationDatabase
from astra_d.conversation.manager import ConversationManager


class MainModuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["ASTRA_D_DATA_DIR"] = self.temp_dir.name
    
        # Reset the conversation system for each test.
        main.CONVERSATION_DB = ConversationDatabase(":memory:")
        main.CONVERSATION_MANAGER = ConversationManager(
            main.CONVERSATION_DB
        )


    def tearDown(self) -> None:
        main.ACTIVE_DOCUMENT = None
        main.ACTIVE_DOCUMENT_PATH = None
        os.environ.pop("ASTRA_D_DATA_DIR", None)
        self.temp_dir.cleanup()

    def test_help_command(self) -> None:
        output = main.dispatch("help")
        self.assertIn("Commands:", output or "")

    def test_quit_returns_none(self) -> None:
        self.assertIsNone(main.dispatch("quit"))

    @patch("main.chat_with_ollama", return_value="Hello from Astra-D")
    def test_chat_command(self, mock_chat) -> None:
        output = main.dispatch("chat hello there")
    
        self.assertEqual(output, "Hello from Astra-D")
        mock_chat.assert_called_once()
    
        history = main.CONVERSATION_MANAGER.get_history()
    
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "hello there")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "Hello from Astra-D")

    @patch("main.chat_with_ollama", return_value="Reply")
    def test_plain_text_routes_to_chat(self, _mock_chat) -> None:
        output = main.dispatch("Tell me a joke")
        self.assertEqual(output, "Reply")

    def test_note_commands(self) -> None:
        create_output = main.dispatch("note add Buy coffee")
        self.assertIn("Note created", create_output or "")
        list_output = main.dispatch("note list")
        self.assertIn("Buy coffee", list_output or "")

        note_id = notes.load_notes()[0]["id"]
        delete_output = main.dispatch(f"note delete {note_id}")
        self.assertIn("deleted", delete_output.lower())

    def test_task_commands(self) -> None:
        create_output = main.dispatch('task add Write docs --desc Update README')
        self.assertIn("Task created", create_output or "")
        task_id = tasks.load_tasks()[0]["id"]
        complete_output = main.dispatch(f"task complete {task_id}")
        self.assertIn("completed", complete_output.lower())
        delete_output = main.dispatch(f"task delete {task_id}")
        self.assertIn("deleted", delete_output.lower())

    def test_search_command(self) -> None:
        output = main.dispatch(f"search {self.temp_dir.name} test")
        self.assertIsNotNone(output)

    @patch("main.retrieval.index_document", return_value=2)
    @patch("main.pdf_utils.file_hash", return_value="dummy_hash")
    @patch("main.pdf_utils.read_pdf", return_value="alpha beta " * 120)
    def test_loadpdf_indexes_document_chunks(
    self,
        _mock_read_pdf,
        _mock_file_hash,
        mock_index,
    ) -> None:
        output = main.dispatch("loadpdf sample.pdf")
        self.assertIn("Indexed 2 chunks", output or "")
        mock_index.assert_called_once()
    

    @patch("main.retrieval.semantic_search")
    def test_retrieve_returns_top_five_semantic_matches(self, mock_search) -> None:
        main.ACTIVE_DOCUMENT_PATH = "sample.pdf"
        mock_search.return_value = [
            main.retrieval.SemanticMatch("alpha chunk", "sample.pdf", 0, 0.1)
        ]

        output = main.dispatch("retrieve alpha")

        mock_search.assert_called_once_with("alpha", top_k=5, source="sample.pdf")
        self.assertIn("alpha chunk", output or "")

    def test_clear_history(self) -> None:
        memory.add_message("user", "hello")
        output = main.dispatch("clear")
        self.assertIn("cleared", output.lower())
        self.assertEqual(memory.load_conversations(), [])

    @patch("main.ollama.chat")
    def test_chat_with_ollama_success(self, mock_chat) -> None:
        mock_chat.return_value = {"message": {"content": "Test response"}}
        reply = main.chat_with_ollama("Hi", [])
        self.assertEqual(reply, "Test response")
        mock_chat.assert_called_once()

    @patch("main.ollama.chat", side_effect=RuntimeError("connection refused"))
    def test_chat_with_ollama_failure(self, _mock_chat) -> None:
        with self.assertRaises(main.OllamaChatError):
            main.chat_with_ollama("Hi", [])


if __name__ == "__main__":
    unittest.main()
