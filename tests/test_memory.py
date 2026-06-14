"""Tests for memory.py."""

import json
import os
import tempfile
import unittest
from pathlib import Path

import memory


class MemoryModuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["ASTRA_D_DATA_DIR"] = self.temp_dir.name

    def tearDown(self) -> None:
        os.environ.pop("ASTRA_D_DATA_DIR", None)
        self.temp_dir.cleanup()

    def test_creates_memory_file_automatically(self) -> None:
        conversations = memory.load_conversations()
        self.assertEqual(conversations, [])
        self.assertTrue(memory.memory_path().exists())

    def test_save_and_load_conversations(self) -> None:
        memory.save_conversations([{"role": "user", "content": "hello"}])
        loaded = memory.load_conversations()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["content"], "hello")

    def test_add_message_appends_and_persists(self) -> None:
        memory.add_message("user", "first")
        memory.add_message("assistant", "second")
        loaded = memory.load_conversations()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[1]["role"], "assistant")

    def test_clear_conversations(self) -> None:
        memory.add_message("user", "hello")
        memory.clear_conversations()
        self.assertEqual(memory.load_conversations(), [])

    def test_invalid_role_raises(self) -> None:
        with self.assertRaises(ValueError):
            memory.add_message("invalid", "hello")

    def test_invalid_json_raises_memory_error(self) -> None:
        path = memory.memory_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{bad json", encoding="utf-8")
        with self.assertRaises(memory.MemoryError):
            memory.load_conversations()

    def test_payload_shape_is_valid(self) -> None:
        memory.save_conversations([])
        payload = json.loads(memory.memory_path().read_text(encoding="utf-8"))
        self.assertIn("conversations", payload)


if __name__ == "__main__":
    unittest.main()
