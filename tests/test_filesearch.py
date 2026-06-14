"""Tests for filesearch.py."""

import os
import tempfile
import unittest
from pathlib import Path

import filesearch


class FileSearchModuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        (root / "README.md").write_text("docs", encoding="utf-8")
        (root / "notes.txt").write_text("notes", encoding="utf-8")
        nested = root / "nested"
        nested.mkdir()
        (nested / "report-final.pdf").write_text("pdf", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_finds_matching_files_recursively(self) -> None:
        results = filesearch.file_search(self.temp_dir.name, "report")
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].endswith("report-final.pdf"))

    def test_case_insensitive_match(self) -> None:
        results = filesearch.file_search(self.temp_dir.name, "readme")
        self.assertEqual(len(results), 1)

    def test_missing_directory_raises(self) -> None:
        with self.assertRaises(filesearch.FileSearchError):
            filesearch.file_search("/path/that/does/not/exist", "file")

    def test_file_path_raises(self) -> None:
        file_path = Path(self.temp_dir.name) / "README.md"
        with self.assertRaises(filesearch.FileSearchError):
            filesearch.file_search(file_path, "read")

    def test_empty_search_string_raises(self) -> None:
        with self.assertRaises(ValueError):
            filesearch.file_search(self.temp_dir.name, "  ")


if __name__ == "__main__":
    unittest.main()
