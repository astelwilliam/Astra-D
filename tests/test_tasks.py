"""Tests for tasks.py."""

import os
import tempfile
import unittest

import tasks


class TasksModuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["ASTRA_D_DATA_DIR"] = self.temp_dir.name

    def tearDown(self) -> None:
        os.environ.pop("ASTRA_D_DATA_DIR", None)
        self.temp_dir.cleanup()

    def test_creates_tasks_file_automatically(self) -> None:
        self.assertEqual(tasks.load_tasks(), [])
        self.assertTrue(tasks.tasks_path().exists())

    def test_create_task(self) -> None:
        created = tasks.create_task("Write tests", "Cover all modules")
        loaded = tasks.load_tasks()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["title"], "Write tests")
        self.assertFalse(loaded[0]["completed"])

    def test_complete_task(self) -> None:
        created = tasks.create_task("Ship feature")
        completed = tasks.complete_task(created["id"])
        self.assertTrue(completed)
        self.assertTrue(tasks.load_tasks()[0]["completed"])
        self.assertIsNotNone(tasks.load_tasks()[0]["completed_at"])

    def test_delete_task(self) -> None:
        created = tasks.create_task("Remove me")
        deleted = tasks.delete_task(created["id"])
        self.assertTrue(deleted)
        self.assertEqual(tasks.load_tasks(), [])

    def test_complete_missing_task_returns_false(self) -> None:
        self.assertFalse(tasks.complete_task("missing-id"))

    def test_empty_title_raises(self) -> None:
        with self.assertRaises(ValueError):
            tasks.create_task("  ")


if __name__ == "__main__":
    unittest.main()
