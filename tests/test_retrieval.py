"""Tests for ChromaDB-backed semantic retrieval."""

import os
import tempfile
import unittest
from unittest.mock import patch

import retrieval


class FakeCollection:
    def __init__(self) -> None:
        self.deleted_where = None
        self.added = {}
        self.queried = {}

    def delete(self, where):
        self.deleted_where = where

    def add(self, ids, documents, embeddings, metadatas):
        self.added = {
            "ids": ids,
            "documents": documents,
            "embeddings": embeddings,
            "metadatas": metadatas,
        }

    def query(self, query_embeddings, n_results, where=None):
        self.queried = {
            "query_embeddings": query_embeddings,
            "n_results": n_results,
            "where": where,
        }
        return {
            "documents": [["first chunk", "second chunk"]],
            "metadatas": [[
                {"source": "doc.pdf", "chunk_index": 0},
                {"source": "doc.pdf", "chunk_index": 1},
            ]],
            "distances": [[0.12, 0.34]],
        }


class RetrievalModuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["ASTRA_D_DATA_DIR"] = self.temp_dir.name

    def tearDown(self) -> None:
        os.environ.pop("ASTRA_D_DATA_DIR", None)
        self.temp_dir.cleanup()

    def test_chunk_document_uses_overlap(self) -> None:
        chunks = retrieval.chunk_document("abcdefghij", chunk_size=4, chunk_overlap=1)
        self.assertEqual(chunks, ["abcd", "defg", "ghij"])

    def test_index_document_stores_chunks_in_chroma(self) -> None:
        fake_collection = FakeCollection()
        with patch("retrieval._get_collection", return_value=fake_collection), patch(
            "retrieval.embed_texts",
            side_effect=lambda texts: [[float(index)] for index, _text in enumerate(texts)],
        ):
            count = retrieval.index_document("doc.pdf", "alpha " * 300)

        self.assertGreaterEqual(count, 1)
        self.assertEqual(len(fake_collection.added["documents"]), count)
        self.assertEqual(len(fake_collection.added["embeddings"]), count)
        self.assertTrue(fake_collection.deleted_where["source"].endswith("doc.pdf"))

    def test_semantic_search_requests_top_five(self) -> None:
        fake_collection = FakeCollection()
        with patch("retrieval._get_collection", return_value=fake_collection), patch(
            "retrieval.embed_texts",
            return_value=[[0.1, 0.2]],
        ):
            matches = retrieval.semantic_search("alpha policy", top_k=5, source="doc.pdf")

        self.assertEqual(fake_collection.queried["n_results"], 5)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0].text, "first chunk")
        self.assertEqual(matches[0].chunk_index, 0)


if __name__ == "__main__":
    unittest.main()
