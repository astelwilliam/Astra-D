"""Tests for main.py command dispatch and Ollama integration."""

import os
import tempfile
import unittest
from unittest.mock import patch

import main
import memory
import notes
import tasks


class MainModuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["ASTRA_D_DATA_DIR"] = self.temp_dir.name

    def tearDown(self) -> None:
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
        history = memory.load_conversations()
        self.assertEqual(len(history), 2)

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
