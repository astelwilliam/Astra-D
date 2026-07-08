"""Embeddings-based document retrieval backed by ChromaDB."""

from __future__ import annotations


import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import ollama
except Exception as exc:  # noqa: BLE001 - keep retrieval importable in tests
    _OLLAMA_IMPORT_ERROR = str(exc)

    class _MissingOllama:
        def embed(self, *args, **kwargs):
            raise RuntimeError(f"Ollama dependency is unavailable: {_OLLAMA_IMPORT_ERROR}")

        def embeddings(self, *args, **kwargs):
            raise RuntimeError(f"Ollama dependency is unavailable: {_OLLAMA_IMPORT_ERROR}")

    ollama = _MissingOllama()
CHROMA_DIRNAME = "chroma"
COLLECTION_NAME = "document_chunks"
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150


class RetrievalError(Exception):
    """Raised when document indexing or retrieval fails."""


@dataclass(frozen=True)
class SemanticMatch:
    """A document chunk returned from vector search."""

    text: str
    source: str
    chunk_index: int
    distance: float | None = None


def _data_dir() -> Path:
    override = os.environ.get("ASTRA_D_DATA_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "data"


def chroma_path() -> Path:
    """Return the directory used for persistent ChromaDB storage."""
    return _data_dir() / CHROMA_DIRNAME


def chunk_document(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping chunks suitable for embedding."""
    clean_text = re.sub(r"\s+", " ", text).strip()
    if not clean_text:
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be non-negative and smaller than chunk_size.")

    chunks: list[str] = []
    start = 0
    while start < len(clean_text):
        end = min(start + chunk_size, len(clean_text))
        chunks.append(clean_text[start:end].strip())
        if end == len(clean_text):
            break
        start = end - chunk_overlap
    return chunks


def _embedding_model() -> str:
    return os.environ.get("ASTRA_D_EMBED_MODEL", DEFAULT_EMBEDDING_MODEL)


def embed_texts(texts: list[str], model: str | None = None) -> list[list[float]]:
    """Create embeddings with Ollama for ChromaDB storage/querying."""
    if not texts:
        return []

    selected_model = model or _embedding_model()
    try:
        if hasattr(ollama, "embed"):
            response = ollama.embed(model=selected_model, input=texts)
            embeddings = response.get("embeddings")
            if embeddings:
                return embeddings

        embeddings = []
        for text in texts:
            response = ollama.embeddings(model=selected_model, prompt=text)
            embedding = response.get("embedding")
            if not embedding:
                raise RetrievalError("Ollama returned an empty embedding.")
            embeddings.append(embedding)
        return embeddings
    except Exception as exc:  # noqa: BLE001 - surface provider errors to CLI
        raise RetrievalError(
            f"Embedding request failed with model '{selected_model}'. "
            f"Install/pull it with: ollama pull {selected_model}. Details: {exc}"
        ) from exc


def _chromadb_module() -> Any:
    try:
        import chromadb  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RetrievalError("ChromaDB is not installed. Run: pip install -r requirements.txt") from exc
    return chromadb


def _get_collection() -> Any:
    chromadb = _chromadb_module()
    path = chroma_path()
    path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(path))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _chunk_ids(source: str, chunks: list[str]) -> list[str]:
    source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
    return [f"{source_hash}-{index}" for index, _chunk in enumerate(chunks)]


def _existing_hash(collection: Any, source_path: str) -> str | None:
    """Return the file_hash already stored for this source, if any."""
    try:
        result = collection.get(where={"source": source_path}, limit=1)
    except Exception:
        return None
    metadatas = result.get("metadatas") or []
    if metadatas and metadatas[0]:
        return metadatas[0].get("file_hash")
    return None


def index_document(source: str, text: str, file_hash: str | None = None) -> int:
    """Store document chunks and embeddings in ChromaDB.

    If file_hash is provided and matches what's already indexed for this
    source, indexing is skipped entirely (no re-embedding, no re-upsert).
    """
    source_path = str(Path(source).expanduser().resolve())
    collection = _get_collection()

    if file_hash is not None:
        existing = _existing_hash(collection, source_path)
        if existing == file_hash:
            existing_count = collection.get(where={"source": source_path})
            return len(existing_count.get("ids") or [])

    chunks = chunk_document(text)
    if not chunks:
        raise RetrievalError("Document has no text to index.")

    try:
        collection.delete(where={"source": source_path})
    except Exception:
        pass

    embeddings = embed_texts(chunks)
    metadatas = [
        {"source": source_path, "chunk_index": index, "file_hash": file_hash or ""}
        for index, _chunk in enumerate(chunks)
    ]
    collection.add(
        ids=_chunk_ids(source_path, chunks),
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return len(chunks)


def semantic_search(query: str, top_k: int = 5, source: str | None = None) -> list[SemanticMatch]:
    """Return the top semantic matches from stored document chunks."""
    if not query.strip():
        raise ValueError("Query cannot be empty.")
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0.")

    collection = _get_collection()
    where = None
    if source:
        where = {"source": str(Path(source).expanduser().resolve())}

    query_result = collection.query(
        query_embeddings=embed_texts([query]),
        n_results=top_k,
        where=where,
    )

    documents = (query_result.get("documents") or [[]])[0]
    metadatas = (query_result.get("metadatas") or [[]])[0]
    distances = (query_result.get("distances") or [[]])[0]

    print("\n===== RETRIEVAL DEBUG =====")
    print(f"Query: {query}")
    print(f"Chunks returned: {len(documents)}")
    for i, doc in enumerate(documents):
        dist = distances[i] if i < len(distances) else "N/A"
        meta = metadatas[i] if i < len(metadatas) else {}
        print(f"\n--- Chunk {i+1} (distance={dist}, chunk_index={meta.get('chunk_index')}) ---")
        print(doc[:500])
    print("===========================\n")

    matches: list[SemanticMatch] = []
    for index, document in enumerate(documents):
        metadata = metadatas[index] if index < len(metadatas) and metadatas[index] else {}
        distance = distances[index] if index < len(distances) else None
        matches.append(
            SemanticMatch(
                text=document,
                source=str(metadata.get("source", "")),
                chunk_index=int(metadata.get("chunk_index", index)),
                distance=distance,
            )
        )
    return matches