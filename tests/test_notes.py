"""Tests for notes.py."""

import os
import tempfile
import unittest

import notes


class NotesModuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["ASTRA_D_DATA_DIR"] = self.temp_dir.name

    def tearDown(self) -> None:
        os.environ.pop("ASTRA_D_DATA_DIR", None)
        self.temp_dir.cleanup()

    def test_creates_notes_file_automatically(self) -> None:
        self.assertEqual(notes.load_notes(), [])
        self.assertTrue(notes.notes_path().exists())

    def test_create_and_view_notes(self) -> None:
        created = notes.create_note("Remember milk")
        loaded = notes.view_notes()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["id"], created["id"])
        self.assertEqual(loaded[0]["content"], "Remember milk")

    def test_delete_note(self) -> None:
        created = notes.create_note("Temporary")
        deleted = notes.delete_note(created["id"])
        self.assertTrue(deleted)
        self.assertEqual(notes.load_notes(), [])

    def test_delete_missing_note_returns_false(self) -> None:
        self.assertFalse(notes.delete_note("missing-id"))

    def test_empty_content_raises(self) -> None:
        with self.assertRaises(ValueError):
            notes.create_note("   ")


if __name__ == "__main__":
    unittest.main()
